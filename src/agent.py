from __future__ import annotations
import json, os
from typing import Dict, List, Tuple, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .utils import de_duplicate
from .models import PageRecord, LinkInfo, MenuItem

class AgentBase:
    def __init__(self):
        self.llm: ChatOpenAI = self._get_llm()
        self._prompt_path: str = ""

    def _load_prompt(self) -> str:
        try:
            with open(self._prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error: Failed to load prompt from {self._prompt_path}: {e}")
            raise e

    def _get_llm(self) -> ChatOpenAI:
        load_dotenv()
        base = os.getenv("OPENAI_API_BASE", "http://localhost:1234/v1")
        key = os.getenv("OPENAI_API_KEY", "sk-noauth")
        model = os.getenv("OPENAI_MODEL", "gpt-oss-20b")
        return ChatOpenAI(model=model, temperature=0.2, base_url=base, api_key=key)

class NoiseClassifier(AgentBase):
    """
    Lightweight noise classifier, used to filter out sure non-menu links.
    The call is lightweight, we are going to use a small classifer model (re)trained on existing data.
    Here we substitute the classifier model with a prompt.
    """
    def __init__(self):
        super().__init__()
        self._prompt_path = "prompts/small_noise_classifier.txt"
        self.NOISE_CONFIDENCE_THRESHOLD = float(os.getenv("NOISE_CONFIDENCE_THRESHOLD", "0.3"))
        self.prompt = self._load_prompt()

    def classify(self, links: List[LinkInfo]) -> List[LinkInfo]:
        # Process links in batches of 20 (otherwise we will exceed the context)

        print(f"Classifying links...")
        print(f"Links: {links}")

        result_links = []
        batch_size = 20
        
        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            
            try:
                # Prepare batch data for the model
                links_data = []
                for link in batch:
                    links_data.append({
                        "url": link.url,
                        "text": link.text
                    })
                
                user_payload = {
                    "links": links_data
                }

                msgs = [
                    SystemMessage(content=self.prompt),
                    HumanMessage(content=json.dumps(user_payload, ensure_ascii=False))
                ]

                resp = self.llm.invoke(msgs)
                raw = resp.content or "{}"
                
                data = json.loads(raw)
                classified_links = data.get("links", [])

                print(f"Classified links: {classified_links}")

                
                # Process each link in the batch
                for j, link_data in enumerate(classified_links):
                    if j < len(batch):
                        original_link = batch[j]
                        confidence = link_data.get("confidence", 1.0)
                        
                        # Only include links that are not noise or have low confidence for noise classification
                        if confidence <= self.NOISE_CONFIDENCE_THRESHOLD:
                            result_links.append(LinkInfo(
                                url=original_link.url,
                                text=original_link.text
                            ))
                                                        
            except Exception as e:
                print(f"Error processing batch {i//batch_size + 1}: {type(e).__name__}: {str(e)}")
                # If there's an error processing a batch, include all links in the batch by default
                for link in batch:
                    result_links.append(LinkInfo(
                        url=link.url,
                        text=link.text
                    ))

        

        return result_links

class MenuClassifier(AgentBase):
    """
    Page classifier, it receives a page content and returns the respective menu type.
    """
    def __init__(self, menutypes: Dict[str,str]):
        super().__init__()
        self._prompt_path = "prompts/menu_classifier.txt"
        self.prompt = self._load_prompt()
        self.menutypes: Dict[str,str] = menutypes
        self.MENU_ITEM_CLASSIFIER_CONFIDENCE_THRESHOLD = float(os.getenv("MENU_ITEM_CLASSIFIER_CONFIDENCE_THRESHOLD", "0.7"))

    def classify(
        self,
        site_name: str,
        site_url: str,
        page_url: str,
        page_text: str,
        page_title: str,
        menutypes: Dict[str,str],
        content_disposition: Optional[str] = None,
    ) -> Optional[MenuItem]:
        """Return single MenuItem object"""
        try:
            # Build compact context
            user_payload = {
                "SITE_NAME": site_name,
                "SITE_URL": site_url,
                "PAGE_URL": page_url,
                "PAGE_CONTENT": page_text,
                "PAGE_TITLE": page_title,
                "MENU_TYPES": menutypes,
                "MENU_FORMATS": ["pdf","viewer","integrated","none"],
                "LANGS": ["de","en","fr","it"],
                "CONTENT_DISPOSITION": content_disposition
            }

            msgs = [
                SystemMessage(content=self.prompt),
                HumanMessage(content=json.dumps(user_payload, ensure_ascii=False))
            ]

            resp = self.llm.invoke(msgs)
            raw = resp.content or "{}"
            try:
                data = json.loads(raw)
                # Parse the response which should contain a "menus" array
                menus = data.get("menus", [])
                
                # If no menus found, return None
                if not menus:
                    return None
                
                # Extract the first menu item from the array
                menu_data = menus[0]
                
                # Check confidence threshold before creating MenuItem
                confidence = menu_data.get("confidence", 0.0)
                if confidence < self.MENU_ITEM_CLASSIFIER_CONFIDENCE_THRESHOLD:
                    return None
                
                # Create MenuItem with the extracted data
                menu_item = MenuItem(
                    link=page_url,  # Use the page URL as the link
                    type_code=menu_data.get("type_code", "oct_menu"),
                    type_label=menutypes.get(menu_data.get("type_code", "oct_menu"), "Unknown"),
                    format=menu_data.get("format", "integrated"),
                    languages=menu_data.get("languages", []),
                    confidence=confidence,
                    notes=menu_data.get("reason", None),
                    content_disposition=content_disposition
                )
                
                # Process languages
                langs = [l.lower()[:2] for l in menu_item.languages]
                menu_item.languages = de_duplicate([l for l in langs if l in ["de","en","fr","it"]])[:3]
                
                return menu_item
            except Exception as e:
                print(f"Error: Failed to parse menu item: {type(e).__name__}: {str(e)}")
                print(f"Raw response that caused error: {raw}")
                return None
        except Exception as e:
            print(f"Error: LLM server unavailable or error occurred: {e}")
            print("Continuing without agent analysis...")
            return None

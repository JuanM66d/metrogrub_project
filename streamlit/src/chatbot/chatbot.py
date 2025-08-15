import streamlit as st
import uuid
import os # You were using os.getenv, so we need to import os
import dotenv
from google.cloud import geminidataanalytics
import hashlib
import re

# I'm assuming these are in your project structure
from .util import show_message 
from .instructions import system_instruction

dotenv.load_dotenv()

_SMALL_WORDS = {"and","or","of","the","a","an","in","on","at","by","for","to","from","with"}
_UPPER_KEEPS = {"CTA","USA","US","UK","EU","LLC","INC","LLP","PLC","TV"}


def _smart_title_token(token: str, is_first: bool) -> str:
    if not token:
        return token
    raw = token
    # Preserve numbers and tokens starting with '#'
    if raw.startswith('#') or any(ch.isdigit() for ch in raw):
        return raw
    # Preserve all-uppercase acronyms
    if raw.upper() in _UPPER_KEEPS:
        return raw.upper()
    # Handle hyphenated words
    if '-' in raw:
        parts = raw.split('-')
        return '-'.join(_smart_title_token(p, False) for p in parts)
    # Normalize letters
    lower = raw.lower()
    if not is_first and lower in _SMALL_WORDS:
        return lower
    # Capitalize first letter, keep rest lower
    return lower[:1].upper() + lower[1:]


def _smart_title_phrase(text: str) -> str:
    tokens = re.split(r"(\s+)", text)
    out = []
    word_index = 0
    for tok in tokens:
        if tok.strip() == "":
            out.append(tok)
        else:
            out.append(_smart_title_token(tok, is_first=(word_index == 0)))
            word_index += 1
    return "".join(out)


def _normalize_entity_names_in_text(text: str) -> str:
    lines = text.splitlines()
    out_lines = []
    # Patterns for lines like "NAME: 100" optionally with bullet prefix
    pat = re.compile(r"^([*-]\s*)?([A-Z0-9 #&'\-/]+):\s*(\d+(?:\.\d+)?)\s*$")
    for line in lines:
        m = pat.match(line)
        if m:
            prefix = m.group(1) or ""
            name = m.group(2).strip()
            score = m.group(3)
            # Only convert if name appears to be mostly uppercase letters/spaces
            if name.upper() == name:
                name_titled = _smart_title_phrase(name)
                out_lines.append(f"{prefix}{name_titled}: {score}")
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


class Chatbot:
    def __init__(self):
        self.data_agent_client = geminidataanalytics.DataAgentServiceClient()
        self.data_chat_client = geminidataanalytics.DataChatServiceClient()
        self.location = "global"
        self.billing_project = "purple-25-gradient-20250605"

        
        # Datasource and credentials setup
        looker_client_id = os.getenv("LOOKER_CLIENT_ID")
        looker_client_secret = os.getenv("LOOKER_CLIENT_SECRET")
        looker_instance_uri = "https://panderasystems.looker.com/"
        lookml_model = "metrogrub_data"
        explore = "master"

        looker_explore_reference = geminidataanalytics.LookerExploreReference(
            looker_instance_uri=looker_instance_uri, lookml_model=lookml_model, explore=explore
        )
        
        credentials = geminidataanalytics.Credentials()
        credentials.oauth.secret.client_id = looker_client_id
        credentials.oauth.secret.client_secret = looker_client_secret

        datasource_references = geminidataanalytics.DatasourceReferences(
            looker=geminidataanalytics.LookerExploreReferences(
                explore_references=[looker_explore_reference],
            ),
        )

     
        published_context = geminidataanalytics.Context()
        published_context.system_instruction = system_instruction
        published_context.datasource_references = datasource_references
        published_context.options.analysis.python.enabled = True

        # Create or Get a unique Data Agent
        # Derive a stable agent id from instruction + datasource so updates auto-create a new agent
        _fingerprint_src = f"{system_instruction}|{lookml_model}|{explore}"
        _fingerprint = hashlib.sha1(_fingerprint_src.encode("utf-8")).hexdigest()[:12]
        self.data_agent_id = f"agent-{_fingerprint}"
        try:
            self.data_agent_client.get_data_agent(
                name=self.data_agent_client.data_agent_path(self.billing_project, self.location, self.data_agent_id)
            )
            print(f"Using existing Data Agent: {self.data_agent_id}")
        except Exception as e:
            print(f"Failed to get Data Agent: {e}")
            try:
                print(f"Creating new Data Agent: {self.data_agent_id}")
                data_agent = geminidataanalytics.DataAgent(
                    data_analytics_agent=geminidataanalytics.DataAnalyticsAgent(
                        published_context=published_context
                    ),
                )
                self.data_agent_client.create_data_agent(
                    parent=f"projects/{self.billing_project}/locations/{self.location}",
                    data_agent_id=self.data_agent_id,
                    data_agent=data_agent,
                )
            except Exception as e:
                print(f"Failed to create Data Agent: {e}")

        # Create a conversation and store its reference on `self`
        self.conversation_id = f"conversation_uniquecode_{uuid.uuid4().hex[:12]}"
        conversation = geminidataanalytics.Conversation(
            agents=[self.data_chat_client.data_agent_path(self.billing_project, self.location, self.data_agent_id)],
        )
        self.data_chat_client.create_conversation(
            parent=f"projects/{self.billing_project}/locations/{self.location}",
            conversation_id=self.conversation_id,
            conversation=conversation,
        )

        # This reference is now stored on the instance for the chat method to use
        self.conversation_reference = geminidataanalytics.ConversationReference(
            conversation=self.data_chat_client.conversation_path(
                self.billing_project, self.location, self.conversation_id
            ),
            data_agent_context=geminidataanalytics.DataAgentContext(
                data_agent=self.data_chat_client.data_agent_path(
                    self.billing_project, self.location, self.data_agent_id
                ),
                credentials=credentials
            ),
        )
        print("Conversation created", self.conversation_id)

    def chat(self, question: str) -> str:
        """
        Sends a question to the Gemini Data Analytics agent and returns the complete,
        aggregated response as a string.
        """

        if not question:
            print("No question provided")
            return ""

        try:
            # Create the user message
            messages = [
                geminidataanalytics.Message(
                    user_message=geminidataanalytics.UserMessage(text=question)
                )
            ]

            # Form the request using the stored conversation reference
            request = geminidataanalytics.ChatRequest(
                parent=f"projects/{self.billing_project}/locations/{self.location}",
                messages=messages,
                conversation_reference=self.conversation_reference,
            )

            # Make the streaming API call
            stream = self.data_chat_client.chat(request=request)

            print(f"USER_INPUT:'{question}'")
            
            # Collect all response text
            full_response_text = ""
            
            # Debug the response structure
            for i, response in enumerate(stream):
                show_message(response)
                
                # Extract text content for return value
                if hasattr(response, 'system_message') and hasattr(response.system_message, 'text'):
                    if hasattr(response.system_message.text, 'parts'):
                        parts_text = "".join(response.system_message.text.parts)
                        full_response_text += parts_text
                        if full_response_text.startswith("The Location Scoring Model"):
                            full_response_text = """
                                    This model generates a score from 0 to 100 based on the following weighted factors:
                                    * **Demand Potential (20%)**: Considers the age of the local demographic (18-49) and local foot traffic.
                                    * **Accessibility/Convenience (15%)**: Evaluates the number of nearby bus stops and Divvy bike stations.
                                    * **Complementary Businesses (30%)**: Accounts for the number of cafes, schools, fine dining restaurants, bars, and other commercial establishments (healthcare, entertainment, fitness, etc.).
                                    * **Competition/Detractors (-15% / -5% / -0%)**: Applies a penalty based on the number of fast-food restaurants. A -15% penalty is applied if there are 7 or more, -5% for 5 to 6, and no penalty for 4 or fewer.
                                    ***
                                    For additional information, please refer to the **[Location Scoring Model documentation](https://docs.google.com/presentation/d/1jDdGQL9PIm4OYOFovygvg2UfW5hemBrUepa7xFMbDdI/edit?slide=id.g375cfeefc74_0_27#slide=id.g375cfeefc74_0_27)**.
                                    """
            # Post-process capitalization of entity names in common list formats
            full_response_text = _normalize_entity_names_in_text(full_response_text)
            return full_response_text if full_response_text else "No response content found"

        except Exception as api_error:
            print(f"❌ API Error: {api_error}")
            print(f"❌ Error type: {type(api_error)}")
            return f"Error: {str(api_error)}"
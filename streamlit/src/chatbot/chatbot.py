from google.cloud import geminidataanalytics
import uuid
from util import show_message
from instructions import system_instruction
import dotenv

dotenv.load_dotenv()

class Chatbot:
    def __init__(self):
        self.data_agent_client = geminidataanalytics.DataAgentServiceClient()
        self.data_chat_client = geminidataanalytics.DataChatServiceClient()
        self.location = "global"
        self.billing_project = "purple-25-gradient-20250605"
        self.bq_project_id = "bigquery-public-data"
        

    def init_chatbot(self):
        data_agent_client = geminidataanalytics.DataAgentServiceClient()
        data_chat_client = geminidataanalytics.DataChatServiceClient()

        location = "global"

        billing_project = "purple-25-gradient-20250605" 

        bq_project_id = "bigquery-public-data"  # @param {type:"string"}
        bq_dataset_id = "faa"  # @param {type:"string"}
        bq_table_id = "us_airports"  # @param {type:"string"}


        looker_client_id = os.getenv("LOOKER_CLIENT_ID")  # @param {type:"string"}
        looker_client_secret = os.getenv("LOOKER_CLIENT_SECRET")  # @param {type:"string"}
        looker_instance_uri = "https://panderasystems.looker.com/"  # @param {type:"string"}
        lookml_model = "metrogrub_data"  # @param {type:"string"}
        explore = "master"  # @param {type:"string"}

        looker_explore_reference = geminidataanalytics.LookerExploreReference(
            looker_instance_uri=looker_instance_uri, lookml_model=lookml_model, explore=explore
        )

        bigquery_table_reference = geminidataanalytics.BigQueryTableReference(
            project_id=bq_project_id, dataset_id=bq_dataset_id, table_id=bq_table_id
        )

        credentials = geminidataanalytics.Credentials()
        credentials.oauth.secret.client_id = looker_client_id
        credentials.oauth.secret.client_secret = looker_client_secret

        datasource_references = geminidataanalytics.DatasourceReferences(
            # bq=geminidataanalytics.BigQueryTableReferences(
            #     table_references=[bigquery_table_reference]
            # ),
            looker=geminidataanalytics.LookerExploreReferences(
                explore_references=[looker_explore_reference],
                # credentials=credentials # Note: uncomment this only in case of stateless chat via inline context
            ),
        )

        # Set up context for stateful chat
        published_context = geminidataanalytics.Context()
        published_context.system_instruction = system_instruction
        published_context.datasource_references = datasource_references
        published_context.options.analysis.python.enabled = True

        data_agent_id = f"agent_{uuid.uuid4().hex[:8]}"


        try: 
            request = geminidataanalytics.GetDataAgentRequest(
                name=data_agent_client.data_agent_path(billing_project, location, data_agent_id)
            )
            response = data_agent_client.get_data_agent(request=request)
            print(response)
        except Exception as e:
            data_agent = geminidataanalytics.DataAgent(
                data_analytics_agent=geminidataanalytics.DataAnalyticsAgent(
                    published_context=published_context
                ),
            )
            request = geminidataanalytics.CreateDataAgentRequest(
                parent=f"projects/{billing_project}/locations/{location}",
                data_agent_id=data_agent_id,  
                data_agent=data_agent,
            )

            try:
                response = data_agent_client.create_data_agent(request=request)
                print(f"Data Agent created:\n\n{response.metadata}")
            except Exception as e:
                print(f"Error creating Data Agent: {e}")


        # Initialize request argument(s)  # @param {type:"string"}
        conversation_id = f"conversation_{uuid.uuid4().hex[:8]}"  # Generate unique ID

        conversation = geminidataanalytics.Conversation(
            agents=[data_chat_client.data_agent_path(billing_project, location, data_agent_id)],
        )



        request = geminidataanalytics.CreateConversationRequest(
            parent=f"projects/{billing_project}/locations/{location}",
            conversation_id=conversation_id,
            conversation=conversation,
        )

        # Make the request
        response = data_chat_client.create_conversation(request=request)

        # Handle the response
        print(response)

        # Create a conversation_reference
        conversation_reference = geminidataanalytics.ConversationReference(
            conversation=data_chat_client.conversation_path(
                billing_project, location, conversation_id
            ),
            data_agent_context=geminidataanalytics.DataAgentContext(
                data_agent=data_chat_client.data_agent_path(
                    billing_project, location, data_agent_id
                ),
                credentials=credentials  # Uncomment if using Looker datasource
            ),
        )

        print("🤖 Chatbot ready! Type 'exit' to quit.")
        print("=" * 50)


while True: 
    try:
        question = input("\n💬 Enter your message: ").strip()

        if question.lower() in ["exit", "quit", "bye"]:
            print("👋 Goodbye!")
            break
        
        if not question:
            print("⚠️  Please enter a message.")
            continue

        # Create the user message
        messages = [
            geminidataanalytics.Message(
                user_message=geminidataanalytics.UserMessage(text=question)
            )
        ]

        # Form the request
        request = geminidataanalytics.ChatRequest(
            parent=f"projects/{billing_project}/locations/{location}",
            messages=messages,
            conversation_reference=conversation_reference,
        )

        print("🔄 Processing your request...")
        
        try:
            # Make the request
            stream = data_chat_client.chat(request=request)

            # Handle the response
            print("🤖 Response:")
            print("-" * 30)
            
            for response in stream:
                try:
                    show_message(response)
                except Exception as msg_error:
                    print(f"⚠️  Error displaying message: {msg_error}")
                    print(f"Raw response: {response}")
                    
        except Exception as api_error:
            print(f"❌ API Error: {api_error}")
            print("🔄 You can try asking again or rephrase your question.")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user. Goodbye!")
        break
    except Exception as general_error:
        print(f"❌ Unexpected error: {general_error}")
        print("🔄 Continuing... You can try asking again.")
        continue

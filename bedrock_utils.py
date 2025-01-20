import json
import boto3
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)
logger = setup_logging()

class BedrockHelper:
    REGION_NAME = "us-east-1"
    MODEL_ALIASES = {
        "s35v2": {"name": "Cloaude 3.5 Sonnet v2", "model_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0"},
        "s35": {"name": "Cloaude 3.5 Sonnet", "model_id": "us.anthropic.claude-3-5-sonnet-20240620-v1:0"},
        "h35": {"name": "Cloaude 3.5 Haiku", "model_id": "us.anthropic.claude-3-5-haiku-20241022-v1:0"},
        "h3": {"name": "Cloaude 3 Haiku", "model_id": "anthropic.claude-3-haiku-20240307-v1:0"},
        "c21": {"name": "Claude 2.1", "model_id": "anthropic.claude-v2:1"},
        "tg1e": {"name": "Titan Text G1 - Express", "model_id": "amazon.titan-text-express-v1"},
        "np": {"name": "Nova Pro", "model_id": "amazon.nova-pro-v1:0"},
        "nl": {"name": "Nova Lite", "model_id": "amazon.nova-lite-v1:0"}
    }

    SYSTEM_PROMPT =  "You are a helpful AI assistant. Be concise and precise in your answers."

    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=self.REGION_NAME)

    def get_model_id(self, model_alias):
        return self.MODEL_ALIASES[model_alias]["model_id"]

    def get_model_name(self, model_alias):
        return self.MODEL_ALIASES[model_alias]["name"]

    def get_model_aliases(self):
        return list(self.MODEL_ALIASES.keys())

    def __get_llm_result(self, model_id, prompt, max_tokens=4096, temperature=0):
        try:
            if "anthropic.claude" in model_id:
                return self.__invoke_claude(model_id, prompt, max_tokens, temperature)
            elif "amazon.titan" in model_id:
                return self.__invoke_titan(model_id, prompt, max_tokens, temperature)
            elif "ai21.j2" in model_id:
                return self.__invoke_ai21(model_id, prompt, max_tokens, temperature)
            elif "cohere.command" in model_id:
                return self.__invoke_cohere(model_id, prompt, max_tokens, temperature)
            elif "amazon.nova" in model_id:
                return self.__invoke_nova(model_id, prompt, max_tokens, temperature)
            else:
                raise ValueError(f"Unsupported model: {model_id}")
        except Exception as e:
            logger.error(f"Error on __get_llm_result: {str(e)}")
            raise

    def get_translated_text(self, model_alias, text, max_tokens=4096, temperature=0):
        model_id = self.get_model_id(model_alias)
        prompt = self.__generate_translate_prompt(text)

        return self.__get_llm_result(model_id, prompt, max_tokens, temperature)

    def get_summarized_text(self, model_alias, text, max_tokens=4096, temperature=0):
        model_id = self.get_model_id(model_alias)
        prompt = self.__generate_summary_prompt(text)

        return self.__get_llm_result(model_id, prompt, max_tokens, temperature)

    def get_insight(self, model_alias, transcripts, question, max_tokens=4096, temperature=0):
        model_id = self.get_model_id(model_alias)
        prompt = self.__generate_insights_prompt(transcripts, question)

        return self.__get_llm_result(model_id, prompt, max_tokens, temperature)

    def get_insight_stream(self, model_alias, transcripts, question, max_tokens=4096, temperature=0):
        model_id = self.get_model_id(model_alias)
        prompt = self.__generate_insights_prompt(transcripts, question)

        messages = [{"role": "user", "content": [{"text": prompt}]}]
        inference_config = {"max_new_tokens": max_tokens, "temperature": temperature}
        system_prompt =  [{"text": "You are an AI assistant that helps analyze video transcripts and provide detailed insights."}]
        body = json.dumps({
            "schemaVersion": "messages-v1",
            "messages": messages,
            "system": system_prompt,
            "inferenceConfig": inference_config
        })

        try:
            response = self.bedrock_client.invoke_model_with_response_stream(modelId=model_id, body=body)
            print("Sending request to Bedrock...")  # Debug print

            for event in response['body']:
                chunk_bytes = event["chunk"]["bytes"]
                chunk = json.loads(chunk_bytes.decode())
                # print(f"Received chunk: {chunk}")  # Debug print

                if "contentBlockDelta" in chunk:
                    yield chunk["contentBlockDelta"]["delta"]["text"]

        except Exception as e:
            raise Exception(f"Error in getting streaming insight: {str(e)}")

    def __invoke_claude(self, model_id, prompt, max_tokens, temperature):
        messages = [{"role": "user", "content": prompt}]
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
            "system": self.SYSTEM_PROMPT
        })
        response = self.bedrock_client.invoke_model(modelId=model_id, body=body)
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']

    def __invoke_nova(self, model_id, prompt, max_tokens, temperature):
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        inference_config = {"max_new_tokens": max_tokens, "temperature": temperature}
        system_prompt =  [{"text": self.SYSTEM_PROMPT}]
        body = json.dumps({
            "schemaVersion": "messages-v1",
            "messages": messages,
            "system": system_prompt,
            "inferenceConfig": inference_config
        })
        # logger.info(f"Sending request to Bedrock with prompt: {messages}")
        response = self.bedrock_client.invoke_model(modelId=model_id, body=body, trace="ENABLED")
        response_body = json.loads(response['body'].read())
        return response_body['output']['message']['content'][0]['text']

    def __invoke_titan(self, model_id, prompt, max_tokens, temperature):
        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": max_tokens,
                "temperature": temperature,
                "topP": 1,
            }
        })
        response = self.bedrock_client.invoke_model(modelId=model_id, body=body)
        response_body = json.loads(response['body'].read())
        return response_body['results'][0]['outputText']

    def __invoke_ai21(self, model_id, prompt, max_tokens, temperature):
        body = json.dumps({
            "prompt": prompt,
            "maxTokens": max_tokens,
            "temperature": temperature,
        })
        response = self.bedrock_client.invoke_model(modelId=model_id, body=body)
        response_body = json.loads(response['body'].read())
        return response_body['completions'][0]['data']['text']

    def __invoke_cohere(self, model_id, prompt, max_tokens, temperature):
        body = json.dumps({
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        })
        response = self.bedrock_client.invoke_model(modelId=model_id, body=body)
        response_body = json.loads(response['body'].read())
        return response_body['generations'][0]['text']

    def __generate_translate_prompt(self, text):
        #Your response must be in Korean.
        return f"""
        <transcript>
        {text}
        </transcript>
    
        당신은 YouTube영상에 대한 내용을 번역하는 번역가입니다.
        <transcript>에 있는 내용을 읽고 번역해 주세요.
        <conditions>에 있는 조건을 준수해주세요.
        번역의 예시는 <example>을 참고해주세요.

        <conditions>
        - <transcript>에 없는 내용은 추가 하지 않습니다.
        - 답변은 반드시 한국어로 해주세요.
        </conditions>

        <example>
        이벤트 기반 아키텍처(EDA)의 힘을 활용하여 strangler 및 leave/layer 패턴으로 기존 애플리케이션을 현대화합니다. 
        이 세션에서는 Amazon EventBridge, AWS Lambda 및 마이크로서비스를 활용하여 기술 부채를 줄이는 동시에 민첩성, 복원력 및 보안을 높이는 방법을 알아봅니다. 
        모놀리식 애플리케이션을 마이크로서비스로 원활하게 분해하여 더 빠른 혁신, 확장성 및 유지 관리를 가능하게 하는 방법을 알아보세요.
        </example>

        """

    def __generate_insights_prompt(self, text, question):
        return f"""
        <transcript>
        {text}
        </transcript>
        
        <transcript>에 있는 내용을 읽고 <question>에 있는 질문에 답해주세요.
        응답은 반드시 한국어로 해야 합니다.
        
        <question>
        {question}
        </question>
        """

    def __generate_summary_prompt(self, text):
        #Your response must be in Korean.
        return f"""
        <transcript>
        {text}
        </transcript>
        
        당신은 YouTube영상에 대한 내용을 정리하는 기자입니다.
        <transcript>에 있는 내용을 읽고 핵심 내용들을 주제별로 정리해 주세요.
        <conditions>에 있는 조건을 준수해주세요.
        답변은 markdown 형식으로 하며, <format>의 형식을 참고해주세요.
        답변 예시인 <example>을 참고하세요.

        <conditions> 
        - 주제와 내용 형식으로 답변해주세요.
        - 내용은 산문으로 서술해주세요.
        - <transcript>에 없는 내용은 추가 하지 않습니다.
        - 답변은 반드시 한국어로 해주세요.
        </conditions>
        
        <format>
        ### [첫 번째 주제]
        * [첫 번째 주제의 내용]
        * [첫 번째 주제의 내용]
        * [첫 번째 주제의 내용]
        ### [두 번째 주제]
        * [두 번째 주제의 내용]
        * [두 번째 주제의 내용]
        * [두 번째 주제의 내용]
        </format>
        
        <example>
        ### 생셩형 AI의 금융 서비스 적용 사례
        * AWS의 생성적 AI는 금융 서비스 산업에서 고객 맞춤형 적용을 통해 비즈니스 결과를 향상시키고 있다.
        * 과거 Bedrock을 통해 세 명의 고객이 생성적 AI를 생산적인 방식으로 활용해온 사례가 공유되었다.
        * Sunlife는 AWS의 프로그램을 활용해 내부 비즈니스 애플리케이션의 ROI를 측정하고, 더 빠르게 시장에 진입할 수 있었다.
        * Natwest는 고객 맞춤형 마케팅과 생성적 AI의 케이스를 통해 클릭률 및 전환율을 높이고, 잘못된 정보와 환각 현상을 줄일 수 있었다.
        ### 금융 서비스 산업에서의 생성적 AI 활용
        * 생성적 AI는 복잡한 문서를 분석하여 금융 서비스 산업에서 실질적인 통찰력을 제공하는 데 도움을 준다. 이를 통해 분석가는 데이터에서 실제적인 인사이트를 도출할 수 있다.
        * 자동화된 규제 준수 프로세스는 인력 소요 시간을 33%에서 60%까지 절감하며, 고객과의 상호작용에서 인사이트를 창출하는 데 효과적이다.
        * 데이터 변환 과정에서 생성적 AI는 ETL 규칙을 작성하고 데이터 변환을 설명하여 고객 onboard 과정을 몇 주로 단축시킬 수 있다. 
        * 금융 서비스의 미래는 더 많은 업무 자동화와 멀티모달 모델 활용으로 특징지어지며, 텍스트뿐 아니라 다양한 매체를 포함하는 모델이 중요하다.
        </example>

        """
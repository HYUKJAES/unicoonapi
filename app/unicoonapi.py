import os
from fastapi import FastAPI, HTTPException, Request, Header, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# 환경변수 로드
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI()

class MissionRequest(BaseModel):
    user_id: str
    keyword: str

# 인증 함수
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key2")

# Supabase에서 user_id 유효성 체크
def is_valid_user(user_id: str) -> bool:
    try:
        response = supabase.table("users").select("id").eq("id", user_id).execute()
        return len(response.data) > 0
    except Exception:
        return False

# GPT 프롬프트 생성
PROMPT_TEMPLATE = '''너는 목표 관리 전문가야\n내가 키워드 하나 줄테니까 키워드와 연관 지어서 아래 내용들을 만들어줘\n\n* 공통내용\n모든 내용은 개조식으로 해줘\n맨 앞에 이모티콘 하나씩 넣어줘\n센스 있는 문구들로 구성해줘\n최대한 간략하게 핵심 단어만 써줘\n\n1. 인생 사명, 미션을 한 줄로 정의해줘. json 키는 horn 이야.\n- 간결하게 20자를 넘지 않도록 해줘\n\n2. 앞에서 정한 인생 사명,미션을 달성하기 위한 목표를 2개 나열해줘. json 키는 cores 야.\n- 목표는 막연한 것 말고 정량적 표시가 가능하고 장기적으로 실천해야하는 항목으로 적어줘\n\n3. 위에서 정한 목표를 달성하기 위한 루틴, 투두를 3개만 나열해줘. json 키는 stars 야.\n- 최대한 간략하게 적어줘\n\n결과를 내보낼 때 ```json 같은 구분 문자 제외한 Json 형태로 만들어서 리턴시킬거야\n\n키워드: {keyword}'''

async def generate_mission(keyword: str) -> str:
    prompt = PROMPT_TEMPLATE.format(keyword=keyword)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content

@app.post("/generate-mission")
async def generate_mission_endpoint(
    req: MissionRequest,
    x_api_key: str = Header(...)
):
    # await verify_api_key(x_api_key)
    # if not is_valid_user(req.user_id):
    #     raise HTTPException(status_code=403, detail="유효하지 않은 사용자입니다.")
    try:
        gpt_result = await generate_mission(req.keyword)
        # Json 파싱 시도 (GPT가 Json으로 반환한다고 가정)
        import json
        try:
            result_json = json.loads(gpt_result)
        except Exception:
            result_json = {"result": gpt_result}
        return JSONResponse(content=result_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

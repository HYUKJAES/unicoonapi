import os
from fastapi import FastAPI, HTTPException, Request, Header, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI
from typing import Any

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
    keyword: Any

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
PROMPT_TEMPLATE = '''
너는 목표 관리 전문가야

내가 키워드 하나 줄테니까 키워드와 연관 지어서 아래 내용들을 만들어줘

* 공통내용
- 모든 내용은 개조식으로 해줘
- 맨 앞에 문구에 어울리는 이모티콘 하나씩 넣어줘
- 센스 있는 문구들로 구성해줘
- 최대한 간략하게 핵심 단어만 써줘

1. 인생 사명, 미션을 한 줄로 정의해줘. json 키는 horn 이야.
   - 간결하게 20자를 넘지 않도록 해줘

2. 앞에서 정한 인생 사명,미션을 달성하기 위한 목표를 2개 나열해줘. json 키는 cores 야.
   - 목표는 막연한 것 말고 정량적 표시가 가능하면서 장기적으로 실천해야하는 항목으로 적어줘
   - 루틴, 투두와 구분해야되. 예를 들어 주 3회 운동은 루틴이야. 봄 마라톤 참석하기는 투두야.
   - 테니스 대회 나가기, 마라톤 수상하기, 7kg 감량, 수면 위생 지키기 등 좀 더 큰 범주를 목표라고 할게
   - 한 문장으로 표현되도록 해야되. 저장되는 테이블에 한 줄짜리 문장으로 들어갈거야.

3. 위에서 정한 목표를 달성하기 위한 루틴, 투두를 3개만 나열해줘. json 키는 stars 야.
   - 최대한 간략하게 적어줘
   - 루틴과 투두는 횟수와 해야하는 것을 구체적인 내용으로 구성
   - 루틴, 투두 구분 없이 깔끔하게 stars 키 안에 배열 3줄로 json 리턴할거야

결과를 내보낼 때 result로 절대 묶지 말아줘.
반드시 예시처럼 JSON만, 코드블록 없이, key와 value 모두 쌍따옴표로 감싸서 리턴해줘.
json 같은 구분 문자 제외하고 앞에서 제시한 key로 구성된 Json 형태로 만들어서 리턴시킬거야.

키워드: {keyword}
'''


# GPT 프롬프트 생성
PROMPT_TEMPLATE2 = '''
너는 목표 관리 전문가야
내가 키워드 하나 줄테니까 키워드와 연관 지어서 아래 내용들을 만들어줘

* 공통내용
- 모든 내용은 개조식으로 해줘
- 맨 앞에 문구에 어울리는 이모티콘 하나씩 넣어줘
- 센스 있는 문구들로 구성해줘
- 최대한 간략하게 핵심 단어만 써줘

제시한 키워드는 인생 사명, 비전이야. 이를 달성하기 위한 목표를 3개 추천, 나열해줘. json 키는 cores 야.
   - 목표는 막연한 것 말고 정량적 표시가 가능하면서 장기적으로 실천해야하는 항목으로 적어줘
   - 루틴, 투두와 구분해야되. 예를 들어 주 3회 운동은 루틴이야. 봄 마라톤 참석하기는 투두야.
   - 테니스 대회 나가기, 마라톤 수상하기, 7kg 감량, 수면 위생 지키기 등 좀 더 큰 범주를 목표라고 할게
   - 한 문장으로 표현되도록 해야되. 저장되는 테이블에 한 줄짜리 문장으로 들어갈거야.

결과를 내보낼 때 result로 절대 묶지 말아줘.
반드시 예시처럼 JSON만, 코드블록 없이, key와 value 모두 쌍따옴표로 감싸서 리턴해줘.
json 같은 구분 문자 제외하고 앞에서 제시한 key로 구성된 Json 형태로 만들어서 리턴시킬거야.

키워드: {keyword}
'''


# GPT 프롬프트 생성
PROMPT_TEMPLATE3 = '''
너는 목표 관리 전문가야
내가 키워드 하나 줄테니까 키워드와 연관 지어서 아래 내용들을 만들어줘

* 공통내용
- 모든 내용은 개조식으로 해줘
- 맨 앞에 문구에 어울리는 이모티콘 하나씩 넣어줘
- 센스 있는 문구들로 구성해줘
- 최대한 간략하게 핵심 단어만 써줘
- 제시한 키워드에서 horn은 인생에서 사명, 비전. cores는 목표, 미션.

제시한 키워드를 달성하기 위해 실천해야하는 루틴, 투두를 3개만 나열해줘. json 키는 stars 야.
   - 제시한 키워드와 루틴, 투두는 다른 내용으로 구체적인 실천사항이야
    예를 들어 1년 내에 목표라면 1달이나 1주 단위로 쪼개서 해야하는 내용을 적어줘
    1달이라면 주간, 매일 실천해야하는 항목을 구체적으로 제시해줘
   - 최대한 간략하게 적어줘
   - 루틴과 투두는 1주에 반복되는 횟수와 해야하는 것을 구체적인 내용으로 구성
   예) 월 3회 유산소 운동, 매일 23:00 취침, 빅데이터분석기사 자격증 취득 등
   - 제시한 키워드를 세부적으로 행동해야하는 실천사항을 정리
   - 루틴, 투두 구분 없이 깔끔하게 stars 키 안에 배열 3줄로 json 리턴할거야

결과를 내보낼 때 result로 절대 묶지 말아줘.
반드시 예시처럼 JSON만, 코드블록 없이, key와 value 모두 쌍따옴표로 감싸서 리턴해줘.
json 같은 구분 문자 제외하고 앞에서 제시한 key로 구성된 Json 형태로 만들어서 리턴시킬거야.

키워드: {keyword}
'''

async def generate_mission(keyword: str) -> str:
    prompt = PROMPT_TEMPLATE.format(keyword=keyword)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

# recommend-cores용 함수
async def generate_cores(keyword: str) -> str:
    prompt = PROMPT_TEMPLATE2.format(keyword=keyword)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

# recommend-stars용 함수
async def generate_stars(keyword) -> str:
    import json
    if isinstance(keyword, dict):
        keyword_str = json.dumps(keyword, ensure_ascii=False)
    else:
        keyword_str = str(keyword)
    prompt = PROMPT_TEMPLATE3.format(keyword=keyword_str)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000
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

@app.post("/recommend-cores")
async def recommend_cores_endpoint(
    req: MissionRequest,
    x_api_key: str = Header(...)
):
    # await verify_api_key(x_api_key)
    # if not is_valid_user(req.user_id):
    #     raise HTTPException(status_code=403, detail="유효하지 않은 사용자입니다.")
    try:
        gpt_result = await generate_cores(req.keyword)
        # Json 파싱 시도 (GPT가 Json으로 반환한다고 가정)
        import json
        try:
            result_json = json.loads(gpt_result)
        except Exception:
            result_json = {"result": gpt_result}
        return JSONResponse(content=result_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend-stars")
async def recommend_stars_endpoint(
    req: MissionRequest,
    x_api_key: str = Header(...)
):
    # await verify_api_key(x_api_key)
    # if not is_valid_user(req.user_id):
    #     raise HTTPException(status_code=403, detail="유효하지 않은 사용자입니다.")
    try:
        gpt_result = await generate_stars(req.keyword)
        # Json 파싱 시도 (GPT가 Json으로 반환한다고 가정)
        import json
        try:
            result_json = json.loads(gpt_result)
        except Exception:
            result_json = {"result": gpt_result}
        return JSONResponse(content=result_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

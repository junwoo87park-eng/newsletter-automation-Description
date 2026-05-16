"""
Claude API를 사용해 뉴스레터 HTML 생성
"""

import anthropic
import json
import os
from datetime import datetime

class NewsletterGenerator:
    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다")
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def create_newsletter(self, crawled_data_path='crawled_data.json'):
        """크롤링된 데이터로 뉴스레터 생성"""
        
        # 크롤링 데이터 로드
        try:
            with open(crawled_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("❌ crawled_data.json 파일을 찾을 수 없습니다")
            return None
        
        items = data.get('items', [])
        
        if not items:
            print("❌ 수집된 뉴스가 없습니다")
            return None
        
        print(f"📊 총 {len(items)}건의 뉴스로 뉴스레터 생성 중...")
        
        # Claude에게 뉴스레터 생성 요청
        prompt = f"""
다음은 이번 주 수집된 중소기업 관련 뉴스 {len(items)}건입니다.

{json.dumps(items, ensure_ascii=False, indent=2)}

**임무**: 협력사 대표님들께 보낼 주간 뉴스레터를 작성해주세요.

**요구사항**:
1. 중요도/긴급도 순으로 상위 5-8개 항목만 선별
2. 다음 카테고리로 분류하고 각 카테고리별로 정리:
   - 🔥 마감임박 지원사업 (D-30 이내, 최우선)
   - ⚖️ 법령/규제 변화 (중대재해법, 노조, 안전보건 등)
   - 💰 금융/세제 혜택
   - 🏭 경영 인사이트
3. 각 뉴스마다:
   - 헤드라인 (20자 이내, 임팩트 있게)
   - 핵심 요약 (3-4문장)
   - "왜 우리 회사에 중요한가?" 설명
   - 행동 지침 (신청 방법, 마감일, 체크리스트)
4. 완전한 HTML 이메일 형식으로 출력

**HTML 템플릿 요구사항**:
- 600px 고정 너비, 모바일 반응형
- 인라인 CSS 사용 (Gmail, Outlook 호환)
- 색상 체계:
  * 메인 강조: #00A9A5 (청록)
  * 경고/마감임박: #FF6B6B (빨강)
  * 법령: #FFD93D (노랑)
  * 배경: #F8F9FA (연한 회색)
- 각 뉴스는 카드 형식 (border-radius: 8px)
- CTA 버튼: 최소 44px 높이 (터치 최적화)
- 마감일이 있으면 D-day 자동 계산해서 배지로 표시
- 푸터에 수신거부 링크 포함

**톤앤매너**:
- "협력사 대표님" 호칭 사용
- 전문용어는 쉽게 풀어서 설명
- 긴급한 것은 강조하되 불안 조장 금지
- 구체적 행동 유도 ("지금 신청하세요", "체크리스트 확인")

**출력 형식**: 
완성된 HTML 코드 전체를 출력하세요. 
<!DOCTYPE html>부터 </html>까지 완전한 형태로.
"""
        
        try:
            print("🤖 Claude API 호출 중...")
            
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            html_content = response.content[0].text
            
            # HTML 저장
            today = datetime.now().strftime('%Y%m%d')
            filename = f"newsletter_{today}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ 뉴스레터 생성 완료: {filename}")
            print(f"📧 파일 크기: {len(html_content):,} bytes")
            
            return html_content
        
        except Exception as e:
            print(f"❌ Claude API 호출 실패: {e}")
            return None

if __name__ == "__main__":
    try:
        generator = NewsletterGenerator()
        newsletter = generator.create_newsletter()
        
        if newsletter:
            print("\n" + "="*50)
            print("🎉 뉴스레터 생성 성공!")
            print("="*50)
            print("\n미리보기 (첫 500자):")
            print(newsletter[:500] + "...")
        else:
            print("\n❌ 뉴스레터 생성 실패")
    
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

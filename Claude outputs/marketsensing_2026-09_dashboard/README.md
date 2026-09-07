# 마켓센싱 지식계층 데모 대시보드 — 배포 & 수정 가이드

이 폴더(`index.html` 하나)가 대시보드 전체입니다. 서버·빌드 필요 없음.

---

## 1. Netlify에 올리기 (가장 쉬운 방법 — 드래그&드롭)

1. https://app.netlify.com 로그인
2. 상단 **Sites** 탭 → 화면 아래 점선 박스(**"Deploy manually / Drag and drop your site folder here"**)
3. **이 `netlify_dashboard` 폴더째로** 그 박스에 끌어다 놓기
4. 몇 초 뒤 `https://랜덤이름.netlify.app` 주소가 생성됨 → 바로 공유 가능
5. (선택) **Site settings → Change site name** 에서 주소를 원하는 이름으로 변경

> 수정 후 다시 올릴 때도 같은 방식으로 폴더를 다시 끌어다 놓으면 덮어써집니다.
> `index.html` 파일 하나만 끌어다 놓아도 됩니다(폴더 대신 파일).

### GitHub 연동으로 올리는 경우(화재 대시보드처럼 자동배포)
- 이 `index.html`을 GitHub 저장소에 올리고, Netlify에서 그 저장소를 **New site from Git**으로 연결하면
  이후 깃 푸시할 때마다 자동 배포됩니다.

---

## 2. 내가 직접 고치기

`index.html`을 메모장/브라우저 편집기/VS Code 등으로 열면 됩니다. 세 군데만 알면 충분해요.

### (1) 색·폰트 바꾸기 → 파일 위쪽 `:root { ... }`
```css
--navy:#13233f;   /* 로고·강조 */
--blue:#2563eb;   /* 포인트색 */
--bg:#f4f6fa;     /* 배경 */
```
값(예: `#2563eb`)만 바꾸면 전체 색이 한 번에 바뀝니다.

### (2) 기사·분석 추가/수정 → 파일 아래쪽 `const ARTICLES = [ ... ]`
기사 한 건 = 객체 하나. 아래 틀을 복사해 붙여 넣고 내용만 바꾸세요.
```js
{
  real:true,                     // 실제 기사면 true / 예시면 false
  source:"매체명", url:"https://기사링크",   // real:false면 null, null 로
  title:"기사 제목",
  summary:"한 줄 요약",
  keywords:["키워드1","키워드2"],
  persp:[                        // 관점(사업기획/상품기획/마케팅) — 여러 개 가능
    { axis:"마케팅", kbid:"KB-260904-004", kbsrc:"김영래",
      rule:"주입한 KB 근거 규칙 한 줄",
      a:{ judgment:"KB 없이 해석(현행)", dec:"채택", decc:"a",
          rationale:"근거", boundary:"경계조건" },
      b:{ judgment:"KB 주입 해석(제안)", dec:"채택", decc:"a",
          rationale:"근거", boundary:"경계조건" } }
  ]
}
```
- `dec` = 판정 표시 텍스트(예: 채택/미게재/보류/신사업 검토)
- `decc` = 판정색: `"a"` 초록 · `"r"` 빨강 · `"h"` 노랑

### (3) 메뉴 이름 → 사이드바 `<nav class="nav"> ... </nav>` 의 텍스트

---

## 3. 참고
- 이 대시보드는 **개념 데모**입니다. A/B 해석은 시드 KB(현업 9건)를 근거로 사람이 작성한 예시이며,
  실제 자동 파이프라인(수집→스코어링→관점분석)이 붙으면 B 자리에 실제 모델 출력이 들어갑니다.
- 디자인은 개발자 MI 대시보드(index.html) 색·폰트·레이아웃 시스템에 맞췄습니다.

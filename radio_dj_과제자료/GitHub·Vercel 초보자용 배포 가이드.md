# GitHub·Vercel 초보자용 배포 가이드

## 1. 배포 전에 알아둘 점

이 프로젝트는 Vercel에서 **정적 React 화면 + 서버리스 API**로 실행된다. 대사 생성과 AI 음성 생성은 API 키가 필요하지만, 키는 브라우저나 GitHub에 올리지 않고 Vercel 환경 변수에만 넣는다.

| 준비물 | 확인 |
|---|---|
| GitHub 계정 | GitHub 웹사이트에 로그인 가능 |
| Vercel 계정 | GitHub 계정으로 가입 또는 로그인 가능 |
| 프로젝트 폴더 | `client/`, `api/`, `server/`, `docs/`, `package.json`, `vercel.json` 포함 |
| LLM API 키 | OpenAI 호환 API 키 1개 |
| ElevenLabs API 키 | 기존 `ELEVENLABS_API_KEY` 값 |

> **중요:** `.env` 파일, API 키, 토큰을 GitHub에 올리면 안 된다. `.gitignore`에 이미 제외 규칙이 포함되어 있다.

## 2. GitHub 새 저장소 만들기

1. [GitHub](https://github.com/)에 로그인하고 오른쪽 위 `+` 버튼에서 **New repository**를 선택한다.
2. Repository name에 `room-radio-dj` 또는 `my-room-radio-dj`를 입력한다.
3. 과제 제출용이면 Public을 선택해도 되며, 기존 프로젝트를 올릴 예정이므로 `Add a README file`, `.gitignore`, License 선택은 비워 둔다.
4. **Create repository**를 누른 뒤, 생성 화면의 HTTPS 주소를 복사한다.

예시 주소: `https://github.com/본인아이디/room-radio-dj.git`

## 3. 프로젝트 업로드

### 방법 A. GitHub Desktop 사용

1. GitHub Desktop을 열고 **File → Add Local Repository**를 누른다.
2. 이 프로젝트 폴더 `room-radio-dj`를 선택한다.
3. 저장소가 아니라는 안내가 나오면 **create a repository**를 눌러 생성한다.
4. 아래쪽 Summary에 `과제용 내 방의 라디오 DJ 첫 업로드`라고 적고 **Commit to main**을 누른다.
5. 상단 **Publish repository**를 누른 뒤, 방금 만든 GitHub 저장소 이름과 연결한다.
6. 브라우저에서 저장소가 열리는지 확인하고 URL을 복사한다.

### 방법 B. 터미널 사용

프로젝트 폴더에서 아래 명령을 순서대로 실행한다. `<내-저장소-주소>`는 GitHub에서 복사한 HTTPS 주소로 바꾼다.

```bash
git init -b main
git add .
git commit -m "과제용 내 방의 라디오 DJ 첫 업로드"
git remote add origin <내-저장소-주소>
git push -u origin main
```

업로드 전 `git status`를 실행해 `.env`, `node_modules`, `dist`가 추가되지 않았는지 확인한다.

## 4. Vercel Git Import 배포

1. [Vercel](https://vercel.com/)에 로그인한다.
2. Dashboard에서 **Add New → Project**를 누른다.
3. **Import Git Repository** 목록에서 방금 만든 `room-radio-dj` 저장소의 **Import**를 누른다.
4. 다음 설정을 확인한다.

| 설정 | 값 |
|---|---|
| Framework Preset | `Vite` |
| Root Directory | `./` |
| Build Command | `pnpm run build:vercel` |
| Output Directory | `dist` |
| Install Command | `pnpm install` |

5. **Environment Variables**를 열고 아래 변수를 Production과 Preview에 모두 추가한다.

| 변수명 | 값 | 설명 |
|---|---|---|
| `OPENAI_API_KEY` | 본인의 LLM API 키 | AI 방송 대사 생성용 서버 전용 키 |
| `LLM_MODEL` | 예: `gpt-4.1-mini` | 사용할 모델 ID. 사용 중인 제공자에 맞게 변경 가능 |
| `ELEVENLABS_API_KEY` | 본인의 ElevenLabs API 키 | AI DJ 음성 생성용 서버 전용 키 |
| `OPENAI_BASE_URL` | 선택 사항 | OpenAI가 아닌 호환 API를 쓸 때의 `/v1` 포함 API 주소 |

6. **Deploy**를 누르고 `Ready` 상태가 될 때까지 기다린다.
7. 표시된 `https://...vercel.app` 주소를 열어 기분 선택 → 사연 입력 → 방송 시작 → ON AIR 대사 → AI 음성 재생을 확인한다.

### 키를 다시 확인하는 방법

`OPENAI_API_KEY` 또는 `ELEVENLABS_API_KEY`가 비어 있으면 화면에는 한국어 오류 안내가 표시된다. Vercel Dashboard의 **Settings → Environment Variables**에서 변수 이름과 Production 선택 여부를 확인한 뒤, **Redeploy**를 실행한다.

## 5. Vercel Git Import 증빙 캡처

과제의 5번 항목은 ‘Vercel에서 GitHub Repository를 사용했다’는 증빙이다. 아래 중 한 화면을 캡처한다.

1. **Vercel Dashboard → 프로젝트 → Settings → Git** 화면에서 GitHub 저장소 이름과 연결 상태가 보이도록 캡처한다.
2. 또는 **Deployments** 화면에서 Git 커밋 이름, `Ready` 상태, 배포 주소가 함께 보이도록 캡처한다.

캡처에는 가능하면 다음 세 정보가 함께 보이게 한다.

| 캡처에 보여야 할 정보 | 이유 |
|---|---|
| GitHub 저장소 이름 | Git Import 기반 배포 증빙 |
| `Ready` 상태 또는 성공 표시 | 배포 성공 증빙 |
| Vercel 배포 주소 | 실제 URL과 연결 확인 |

> API 키 값은 캡처에 나오지 않게 한다. Environment Variables 화면은 변수 이름만 보이게 하거나 캡처 대상에서 제외한다.

## 6. 제출 전 최종 체크

| 제출물 | 최종 확인 |
|---|---|
| 웹앱 설명서 PDF | 제목·제작 의도·아키텍처·기술 스택·프롬프트·PMI가 모두 있음 |
| PRD PDF | 기능 요구사항·오류 처리·테스트·제출 계획이 있음 |
| GitHub URL | 새 탭에서 소스 코드와 `README.md`가 열림 |
| Vercel URL | 사연을 입력해 ON AIR 대사가 생성되고 음성이 재생됨 |
| Git Import 증빙 캡처 | 저장소 이름·Ready 상태·Vercel 화면이 함께 보임 |
| 제출 문서 자리표시자 | 이름·GitHub URL·Vercel URL을 본인 정보로 변경함 |

## 7. 자주 생기는 문제

| 증상 | 원인 | 해결 |
|---|---|---|
| Vercel 빌드가 실패함 | pnpm 설치 또는 빌드 설정 오류 | Build Command를 `pnpm run build:vercel`, Output Directory를 `dist`로 확인한다. |
| 방송 대사가 생성되지 않음 | `OPENAI_API_KEY` 또는 모델 ID 오류 | Vercel 환경 변수와 `LLM_MODEL` 값을 확인한 뒤 Redeploy한다. |
| AI DJ 음성이 나오지 않음 | `ELEVENLABS_API_KEY` 누락·잔여 크레딧 부족 | 키 이름·환경 선택·ElevenLabs 크레딧을 확인한다. |
| GitHub에 키를 올린 것 같음 | `.env`를 추적함 | 즉시 키를 폐기·재발급하고 `.env`를 Git 기록에서 제거한다. |
| 새 코드가 URL에 반영되지 않음 | Git push 또는 자동 배포 미완료 | GitHub `main` 브랜치에 push했는지, Vercel Deployments가 `Ready`인지 확인한다. |

---

Vercel의 Vite 배포와 Node.js Functions는 Git 저장소 Import, `pnpm-lock.yaml` 기반 설치, 서버리스 API 경로를 지원한다.[1] [2]

[1]: https://vercel.com/docs/frameworks/frontend/vite
[2]: https://vercel.com/docs/functions/runtimes/node-js

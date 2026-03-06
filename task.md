# 교육공무직 채용 계약서 자동생성 시스템 프롬프트 가이드

교육공무직원 신규 채용 시 **엑셀 기초 데이터 → 한글(HWPX) 계약서 자동 생성**을 수행하는 자동화 시스템을 구축한다.
사용자는 프로그램 실행 후 **엑셀 파일 + 한글 계약서 양식(HWPX)** 을 선택하면, 계약서 내 `{{이름}}`, `{{생일}}`, `{{주소}}` 등의 템플릿 변수에 엑셀 데이터를 자동으로 삽입하여 **완성된 HWPX 계약서 파일을 생성**한다.

본 시스템은 **Claude Code Agent 구조 + Skill 구조 기반 자동화 프로젝트**로 설계되며 다음을 목표로 한다.

* Excel 기반 채용정보 자동 읽기
* HWPX 템플릿 변수 치환
* 다수 계약서 일괄 생성
* 코드 품질 검증 자동화
* exe 배포 패키징

입력 → 출력 흐름

```
엑셀 + HWPX 템플릿 선택
        │
        ▼
엑셀 데이터 파싱
        │
        ▼
HWPX 템플릿 변수 매핑
        │
        ▼
계약서 자동 생성
        │
        ▼
outputs 폴더에 HWPX 파일 생성
        │
        ▼
EXE 패키징 배포
```

---

# 2. 프로젝트 구조 (폴더 트리)

```
contract-generator/

.claude/
│
├── agents/
│   ├── orchestrator.md
│   ├── planner.md
│   ├── coder.md
│   ├── reviewer.md
│   ├── packaging-agent.md
│   └── taskmaster-agent.md
│
├── skills/
│   ├── excel-parser/
│   │   └── SKILL.md
│   │
│   ├── hwpx-generator/
│   │   └── SKILL.md
│   │
│   ├── gui-file-selector/
│   │   └── SKILL.md
│   │
│   ├── exe-packager/
│   │   └── SKILL.md
│   │
│   └── code-review/
│       └── SKILL.md
│
├── commands/
│   └── build-contract-system.md
│
└── settings.json


docs/
├── prd.md
└── task.md


src/
├── main.py
├── gui.py
├── excel_reader.py
├── hwpx_writer.py
├── template_mapper.py
└── contract_pipeline.py


scripts/
├── build_exe.py
└── test_pipeline.py


outputs/
└── contracts/
```

---

# 3. 전체 워크플로우

```
[사용자 입력]
엑셀 파일 + 계약서 HWPX 템플릿 선택
        │
        ▼
┌──────────────────────────────────────┐
│ planner                              │
│ - 요구사항 분석                      │
│ - prd.md 작성                        │
│ - task.md 생성                       │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ taskmaster-agent                     │
│ - 작업 세분화                        │
│ - 단계별 task 생성                   │
│ - 우선순위 정렬                      │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ coder                                │
│ - Python 모듈 작성                   │
│ - Excel 파싱                         │
│ - HWPX 생성                          │
│ - GUI 구현                           │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ reviewer                             │
│ - 코드 리뷰                          │
│ - 오류 검증                          │
│ - 품질 검사                          │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│ packaging-agent                      │
│ - PyInstaller EXE 패키징             │
│ - 배포 파일 생성                     │
└──────────────────────────────────────┘
        │
        ▼
[outputs/contracts]
HWPX 계약서 자동 생성
```

---

# 4. 에이전트 설계 원칙

에이전트 설계 원칙

[https://code.claude.com/docs/ko/sub-agents](https://code.claude.com/docs/ko/sub-agents)

클로드 코드의 공식 가이드라인을 참고해 설계한다.

---

## 1. orchestrator

**역할**

전체 프로젝트 관리 및 에이전트 호출

**description**

USE PROACTIVELY
전체 자동화 시스템의 실행을 관리하고 모든 sub-agent를 호출한다.

**사용 스킬**

* excel-parser
* hwpx-generator
* code-review
* exe-packager

**입력**

```
엑셀 파일 경로
HWPX 템플릿 경로
```

**출력**

```
생성된 계약서 목록
outputs/contracts/*.hwpx
```

**검수 기준**

* 모든 계약서 정상 생성
* 파일명 중복 없음
* 변수 치환 누락 없음

---

## 2. planner

**역할**

요구사항 분석 및 PRD 작성

**언제 호출**

프로젝트 시작 시 MUST BE USED

**출력**

```
docs/prd.md
docs/task.md
```

---

## 3. taskmaster-agent

**역할**

task.md 기반 작업 세분화

**기능**

* task breakdown
* dependency 정리
* 병렬 작업 정의

---

## 4. coder

**역할**

실제 Python 코드 작성

**출력**

```
src/*.py
scripts/*.py
```

---

## 5. reviewer

**역할**

코드 품질 검증

**검증 항목**

* syntax error
* runtime error
* architecture consistency
* 중복 코드

출력

```
review-report.md
```

---

## 6. packaging-agent

**역할**

프로그램 배포용 EXE 생성

**기능**

* PyInstaller 사용
* exe 빌드
* 배포 폴더 생성

---

# 5. Skill 설계

Skill 설계

설계원칙: [https://code.claude.com/docs/ko/skills](https://code.claude.com/docs/ko/skills)

Claude Code 공식 가이드 문서를 반드시 따른다.

---

# Skill 1 — excel-parser

언제 사용되는지

엑셀 채용 데이터를 읽어올 때 사용

SKILL.md 구조

```yaml
---
name: excel-parser
description: |
  채용 엑셀 파일을 읽어 계약서 생성용 데이터를 추출합니다.
  Excel 데이터 파싱이 필요할 때 사용합니다.
allowed-tools:
  - Read
  - Write
  - Bash
model: sonnet
---
```

Usage

```
순 / 직종 / 수험번호 / 이름 / 생일 / 전화 / 임용일 / 주소
```

출력

```
JSON 형태 데이터
```

---

# Skill 2 — hwpx-generator

사용 시점

계약서 템플릿을 채워 HWPX 생성

기능

* 템플릿 변수 치환
* 다중 계약서 생성

예시 변수

```
{{이름}}
{{생일}}
{{전화}}
{{주소}}
{{임용일}}
```

---

# Skill 3 — gui-file-selector

사용 시점

프로그램 실행 시 파일 선택

기능

```
엑셀 파일 선택
HWPX 템플릿 선택
```

기술

```
Python tkinter
```

---

# Skill 4 — exe-packager

기능

Python 프로그램을 EXE로 패키징

사용 도구

```
PyInstaller
```

출력

```
dist/contract-generator.exe
```

---

# Skill 5 — code-review

기능

코드 품질 검증

검증

```
syntax
logic
error handling
```

---

# 6. 단계별 빌드 프롬프트

## 0단계 — Claude Code 규칙 확인

```
Claude Code 공식 Agent / Skill 구조를 확인하고
이 프로젝트의 구조를 분석해줘.

요구사항
- Excel → HWPX 계약서 생성
- GUI 파일 선택
- EXE 패키징

폴더 구조 설계해줘.
```

---

## 1단계 — 아키텍처 설계

```
엑셀 데이터를 기반으로 HWPX 계약서를 생성하는 Python 프로그램 아키텍처를 설계해줘.

요구사항

Excel
1행 헤더

순
직종
수험번호
이름
생일
전화
임용일
주소

HWPX 템플릿 변수

{{이름}}
{{생일}}
{{전화}}
{{주소}}
{{임용일}}

각 행마다 계약서를 생성한다.
```

---

## 2단계 — 코드 생성

```
다음 Python 모듈을 생성해줘

src/

excel_reader.py
hwpx_writer.py
template_mapper.py
gui.py
main.py

요구사항

- pandas 사용
- tkinter GUI
- hwpx xml 기반 파싱
```

---

## 3단계 — Skill 생성

```
.claude/skills/

excel-parser
hwpx-generator
gui-file-selector
exe-packager
code-review

각 스킬에 SKILL.md 생성해줘.
```

---

## 4단계 — Agent 생성

```
.claude/agents/

orchestrator.md
planner.md
coder.md
reviewer.md
packaging-agent.md
taskmaster-agent.md

각 agent YAML frontmatter 포함.
```

---

## 5단계 — Command 생성

```
/build-contract-system

명령 실행 시

1 PRD 작성
2 task 생성
3 코드 작성
4 코드 리뷰
5 EXE 빌드
```

---

## 6단계 — 테스트 실행

```
샘플 Excel 데이터로 테스트 실행

10명의 채용 데이터로 계약서 생성

outputs/contracts 폴더 확인
```

---

# 7. 전체 원샷 프롬프트

```
교육공무직 채용 계약서 자동 생성 시스템을 만들어줘.

요구사항

1 Excel 데이터 기반
2 HWPX 계약서 템플릿 자동 작성
3 GUI 파일 선택
4 Python 기반
5 PyInstaller EXE 배포

Claude Code Agent 구조

.claude/agents/
.claude/skills/
.claude/commands/

필수 기능

Excel → JSON
JSON → HWPX 템플릿 매핑
계약서 자동 생성
EXE 패키징

모든 코드와 Agent Skill을 생성해줘.
```

---

# 8. 체크리스트 & 템플릿

## SKILL.md 템플릿

```
---
name: skill-name
description: 설명
allowed-tools:
  - Read
  - Write
  - Bash
---

# Skill

설명

## Usage

예시 코드
```

---

## agent.md 템플릿

```
---
name: agent-name
description: |
  역할 설명
  MUST BE USED
tools:
  - Read
  - Write
model: sonnet
---

시스템 프롬프트 작성
```

---

# 디버깅 가이드

문제 발생 시 확인

1 Excel 컬럼명
2 템플릿 변수
3 HWPX XML 구조
4 파일 인코딩

---

# 흔한 실수

```
엑셀 헤더 불일치
템플릿 변수 오타
HWPX XML 경로 오류
PyInstaller 누락
```

---

TODO

* HWPX 내부 XML 정확한 경로 확인
* 계약서 파일명 규칙 정의
* GUI UX 상세 설계
* 로그 시스템 추가
* 배포용 설치 프로그램 여부 결정

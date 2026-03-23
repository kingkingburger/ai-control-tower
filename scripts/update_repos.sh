#!/bin/bash
# GitHub 레포 description + topics 일괄 업데이트

update_repo() {
  local name="$1"
  local desc="$2"
  shift 2
  local topics=("$@")

  echo ">>> $name"

  if [ -n "$desc" ]; then
    gh repo edit "kingkingburger/$name" --description "$desc" 2>&1
  fi

  for topic in "${topics[@]}"; do
    gh repo edit "kingkingburger/$name" --add-topic "$topic" 2>&1
  done

  echo ""
}

# ── 프로덕트/서비스 ──

update_repo "ai-control-tower" \
  "AI 도구/플러그인/스킬 실험용 작업 공간 | 워크플로우 프로토타이핑 & 의사결정 시뮬레이션" \
  ai claude-code experiment sandbox workflow

update_repo "sotto" \
  "도시락 메뉴 추천 & 레시피 서비스" \
  typescript nextjs recipe meal-prep

update_repo "framepick" \
  "YouTube 영상 자막 구간별 프레임 캡쳐 데스크톱 앱 | Tauri + Rust" \
  rust tauri youtube screenshot desktop-app frame-capture

update_repo "takoyaki" \
  "Slack 봇으로 회의실 예약 관리" \
  typescript slack slack-bot booking

update_repo "hooky" \
  "썸네일 이미지 간편 생성 웹앱" \
  typescript thumbnail image-generator web-app

update_repo "nofl" \
  "LoL 소환사 주문(플래시) 타이머 체크 서비스" \
  javascript league-of-legends lol game-tool

update_repo "lol-spell-checker" \
  "LoL 소환사 주문 쿨다운 체커" \
  html javascript league-of-legends lol

update_repo "my-notion-task-deadline-manager" \
  "Notion 할일 마감일 → Slack 알림 자동화" \
  typescript notion slack automation task-manager

update_repo "oinqueue" \
  "오인큐 — 실시간 정보 대시보드" \
  typescript dashboard

update_repo "OrderNexus" \
  "주문/거래처 관리 서비스" \
  typescript order-management erp

update_repo "logistic-server" \
  "물류 관리 백엔드 서버" \
  typescript logistics backend

update_repo "ganadala" \
  "한글 자모 분리/조합 라이브러리 (Rust)" \
  rust korean hangul text-processing

update_repo "obsidian_note" \
  "Obsidian vault — Google Drive 동기화" \
  obsidian note-taking knowledge-management

update_repo "leitner_box" \
  "라이트너 상자 — 간격 반복 학습 시스템" \
  typescript spaced-repetition learning education

# ── 게임 ──

update_repo "DinoGame" \
  "크롬 공룡게임 클론 (JavaScript)" \
  javascript game clone dino-game

update_repo "Kartrider" \
  "카트라이더 프로젝트" \
  csharp game unity

update_repo "Horse-Race-Result" \
  "경마 결과 조회 서비스" \
  typescript data-visualization

# ── 클론/학습 프로젝트 ──

update_repo "next13-discord-clone" \
  "Discord 클론 (Next.js 13)" \
  typescript nextjs discord clone

update_repo "next14-jira-clone" \
  "Jira 클론 (Next.js 14)" \
  typescript nextjs jira clone project-management

update_repo "champion-selection-helper-front" \
  "LoL 챔피언 픽 추천 서비스 — 프론트엔드 (Vue)" \
  vue league-of-legends lol frontend

update_repo "champion-selection-helper-server" \
  "LoL 챔피언 픽 추천 서비스 — 백엔드 (NestJS)" \
  typescript nestjs league-of-legends lol backend

update_repo "nodeCreatingBoard" \
  "게시판 만들기 (Node + Express + Vue + MariaDB)" \
  vue nodejs express mariadb crud

update_repo "spring_create_board" \
  "게시판 만들기 (Spring Boot)" \
  java spring-boot crud

update_repo "CD_Back" \
  "캡스톤 디자인 — 백엔드 서버" \
  javascript nodejs backend capstone

update_repo "CD_Front" \
  "캡스톤 디자인 — 프론트엔드 (React)" \
  javascript react frontend capstone

# ── 학습/실험 ──

update_repo "learn-rust-v1" \
  "Rust 학습 프로젝트" \
  rust learning

update_repo "quick-guide-rust-programming" \
  "Rust 빠르게 시작하기 — 학습 노트" \
  rust learning tutorial

update_repo "learn_refactoring" \
  "리팩토링 (Martin Fowler) 학습 정리" \
  javascript refactoring clean-code learning

update_repo "learn_nestJs" \
  "NestJS 학습 프로젝트" \
  typescript nestjs learning

update_repo "learn_React-Native" \
  "React Native 모바일 개발 학습" \
  typescript react-native mobile learning

update_repo "Learn-the-basics-of-vue" \
  "Vue.js 기초 학습" \
  vue learning

update_repo "nestjs-prisma-playground" \
  "NestJS + Prisma 실험 공간" \
  typescript nestjs prisma playground

update_repo "nestjs-kafka-spring" \
  "메시지 큐 학습 — NestJS + Kafka + Spring" \
  java typescript nestjs kafka spring-boot message-queue

update_repo "elasticsearch-practice" \
  "Elasticsearch 실습 프로젝트" \
  python elasticsearch search learning

update_repo "next14-custom-playground" \
  "Next.js 14 실험 공간" \
  typescript nextjs playground

update_repo "next15_playground" \
  "Next.js 15 실험 공간" \
  typescript nextjs playground

update_repo "next15_pomodoro" \
  "뽀모도로 타이머 웹앱 (Next.js 15)" \
  typescript nextjs pomodoro timer productivity

update_repo "spring_boot3_2024" \
  "Spring Boot 3 학습 (2024)" \
  java spring-boot learning

update_repo "react-begin" \
  "React 입문 학습" \
  javascript react learning

update_repo "react-webgame" \
  "React로 만드는 미니 웹게임 모음" \
  javascript react game learning

update_repo "nodejs-book" \
  "Node.js 교과서 학습 정리" \
  javascript nodejs learning

update_repo "java_basic_2024" \
  "Java 기초 학습 (2024)" \
  java learning

# ── 시뮬레이션/데이터 ──

update_repo "salabim" \
  "Salabim — 이산 사건 시뮬레이션 (DES)" \
  python simulation discrete-event-simulation

update_repo "python_simulation_piece" \
  "Python 시뮬레이션 코드 모음" \
  python simulation

update_repo "simulation-docker" \
  "시뮬레이션 환경 Docker 구성" \
  docker simulation devops

update_repo "python_scraping" \
  "Python 웹 스크래핑 연습" \
  python web-scraping

# ── 기타 ──

update_repo "tsboard" \
  "Type-Safe 커뮤니티 게시판 빌더" \
  typescript community forum type-safe

update_repo "my-nest-boilerplate" \
  "NestJS + Prisma + PostgreSQL 보일러플레이트" \
  typescript nestjs prisma postgresql boilerplate

update_repo "small-footprint" \
  "조그만한 흔적 — 개인 프로젝트" \
  typescript

update_repo "Today_I_Learn" \
  "TIL — 매일 배운 것을 정리하는 공간" \
  python til learning

update_repo "Algorithm_Practise" \
  "알고리즘 문제 풀이 연습장" \
  python algorithm problem-solving

update_repo "Algorithm_Study" \
  "알고리즘 스터디 풀이 모음" \
  java algorithm problem-solving study

update_repo "My-PortFolio" \
  "2022 개인 포트폴리오 웹사이트" \
  scss portfolio website

update_repo "Project-Util" \
  "프로젝트 관련 문서 및 유틸리티 모음" \
  documentation

update_repo "my_music" \
  "음악 프로젝트" \
  music

update_repo "kingkingburger" \
  "GitHub 프로필 README" \
  profile readme

update_repo "mini-homepage" \
  "미니 홈페이지 프로젝트" \
  html css

update_repo "Loc8r_web" \
  "Loc8r — 위치 기반 웹앱 (Getting MEAN 학습)" \
  html nodejs learning

update_repo "dev_dignity" \
  "개발자 품격 — 학습 프로젝트" \
  html learning

update_repo "webproject" \
  "웹 프로젝트 (Java)" \
  java web

echo "=== 완료 ==="

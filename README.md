# MyBackupStyle — Windows Backup Suite (Monthly Mirror + Daily Incremental)

**KO | EN below**

Windows 환경에서 **월 1회 미러링**과 **일 1회 증분** 백업을 자동 수행하는 스크립트 세트입니다.  
로그 기록, 30일 경과 파일 ZIP 보관, 90일 지난 ZIP 정리 포함.

## 기능
- Daily: 변경 파일만 복사(증분) + 30일 지난 파일 ZIP 보관 + 90일 지난 ZIP 삭제
- Monthly: `robocopy /MIR` 기반 **미러링** (삭제/변경 동기화)
- 로그 자동 생성, 제외 폴더/확장자 설정 가능

## 구조
```
scripts/
  backup_incremental.py     # 매일 증분
  mirror_monthly.ps1        # 매월 미러링
  install_tasks.ps1         # 작업 스케줄러 자동 등록
  config.json.example       # 설정 예시 (실사용: config.json으로 복사)
```
- 실제 `scripts/config.json`은 커밋하지 마세요(`.gitignore`에 포함).

## 빠른 시작
1) `scripts/config.json.example` → `scripts/config.json` 복사 후 경로/보존정책 수정:
```json
{
  "source": "C:/Data",
  "dest": "D:/Backups/mirror",
  "archive_root": "D:/Backups/archive",
  "retention_days": 30,
  "cleanup_archive_older_days": 90,
  "log_dir": "C:/BackupSuite/logs",
  "excludes": ["Temp", ".cache"],
  "exclude_ext": [".tmp", ".log", ".bak"]
}
```

2) PowerShell(관리자)에서 스케줄러 등록:
```powershell
Set-ExecutionPolicy Bypass -Scope LocalMachine -Force
cd .\scripts
.\install_tasks.ps1
```
- 기본 스케줄: 증분 **매일 01:30**, 미러링 **매월 1일 02:30** (스크립트 내 수정 가능)

## 수동 실행
```powershell
# 증분
py .\scripts\backup_incremental.py

# 미러링
powershell -ExecutionPolicy Bypass -File .\scripts\mirror_monthly.ps1
```

## 팁
- NTFS 권한 보존 필요 시 미러링에 `/COPY:DATSO /SEC` 고려.
- OST/PST/DB 등 잠긴 파일은 VSS 연동 권장.
- 분기 1회 **복구 리허설**로 무결성 확인.

## 라이선스
MIT License (see `LICENSE`)

---

## EN

Windows backup suite for **monthly mirror** and **daily incremental** on Windows.  
Includes logging, 30-day ZIP archival, 90-day archive cleanup.

### Quick Start
1) Copy `scripts/config.json.example` → `scripts/config.json`, adjust paths/policies.  
2) In elevated PowerShell:
```powershell
Set-ExecutionPolicy Bypass -Scope LocalMachine -Force
cd .\scripts
.\install_tasks.ps1
```
- Schedules: Daily 01:30 incremental, Monthly 02:30 (day 1) mirror.

### Notes
- Do **not** commit real `config.json` or logs/archives.
- Consider `/COPY:DATSO /SEC` for ACLs.
- Use VSS for locked files (OST/PST/DB).


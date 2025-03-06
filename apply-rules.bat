@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

echo 디버그: 스크립트 시작됨

REM 현재 디렉토리를 기본 대상으로 설정
set "TARGET_DIR=%CD%"

REM 명령줄 인수가 제공된 경우 해당 디렉토리를 사용
if not "%~1"=="" (
    set "TARGET_DIR=%~1"
)

echo 디버그: 대상 디렉토리 = %TARGET_DIR%

REM 소스 디렉토리 설정 (스크립트가 있는 위치)
set "SOURCE_DIR=%~dp0"
set "SOURCE_DIR=%SOURCE_DIR:~0,-1%"

echo 디버그: 소스 디렉토리 = %SOURCE_DIR%

REM .cursor\rules 폴더를 대상 디렉토리에 확실히 생성
echo 📁 .cursor\rules 폴더 생성 중...
if not exist "%TARGET_DIR%\.cursor\" (
    mkdir "%TARGET_DIR%\.cursor"
    echo - .cursor 폴더 생성됨
)
if not exist "%TARGET_DIR%\.cursor\rules\" (
    mkdir "%TARGET_DIR%\.cursor\rules"
    echo - .cursor\rules 폴더 생성됨
)

REM 소스 디렉토리의 korean 폴더에서 마크다운 파일을 찾아 .mdc로 변환하여 복사
echo 🔄 korean 폴더의 마크다운 파일을 Cursor 규칙으로 변환 중...

set "KOREAN_FOUND=false"

REM 소스 디렉토리의 korean 폴더 처리
if exist "%SOURCE_DIR%\korean\" (
    echo 소스 폴더에서 korean 찾음: %SOURCE_DIR%\korean\
    set "KOREAN_FOUND=true"
    for %%F in ("%SOURCE_DIR%\korean\*.md") do (
        set "mdfile=%%~nxF"
        set "mdcfile=%%~nF.mdc"
        
        echo - 처리 중: %%~nxF
        
        REM 파일을 .mdc 확장자로 복사하면서 내용 전송
        copy "%%F" "%TARGET_DIR%\.cursor\rules\!mdcfile!" >nul
        if !errorlevel! equ 0 (
            echo - %%~nxF 를 .cursor\rules\!mdcfile!로 변환 완료
        ) else (
            echo - %%~nxF 변환 실패 (오류 코드: !errorlevel!)
        )
    )
)

REM 타겟 디렉토리의 korean 폴더 처리 (소스 디렉토리에서 찾지 못한 경우에도 실행)
if exist "%TARGET_DIR%\korean\" (
    echo 대상 폴더에서 korean 찾음: %TARGET_DIR%\korean\
    set "KOREAN_FOUND=true"
    for %%F in ("%TARGET_DIR%\korean\*.md") do (
        set "mdfile=%%~nxF"
        set "mdcfile=%%~nF.mdc"
        
        echo - 처리 중: %%~nxF
        
        REM 파일을 .mdc 확장자로 복사하면서 내용 전송
        copy "%%F" "%TARGET_DIR%\.cursor\rules\!mdcfile!" >nul
        if !errorlevel! equ 0 (
            echo - %%~nxF 를 .cursor\rules\!mdcfile!로 변환 완료
        ) else (
            echo - %%~nxF 변환 실패 (오류 코드: !errorlevel!)
        )
    )
)

if "!KOREAN_FOUND!"=="false" (
    echo 소스나 대상 디렉토리에서 korean 폴더를 찾을 수 없습니다. 파일 변환을 건너뜁니다.
)

REM 대상 디렉토리가 존재하는지 확인하고, README.md 초기화
if not exist "%TARGET_DIR%\" (
    echo 📁 새 프로젝트 디렉토리 생성 중: %TARGET_DIR%
    mkdir "%TARGET_DIR%"
    (
        echo # 새 프로젝트
        echo,
        echo 이 프로젝트는 [cursor-auto-rules-agile-workflow](https://github.com/bmadcode/cursor-auto-rules-agile-workflow)에서 구성된 애자일 워크플로우 지원 및 자동 규칙 생성으로 초기화되었습니다.
        echo,
        echo 워크플로우 문서는 [워크플로우 규칙](docs/workflow-rules.md)을 참조하세요.
    ) > "%TARGET_DIR%\README.md"
)

REM 소스 디렉토리에서 규칙 파일 복사 (기존 파일 덮어쓰지 않음)
echo 📦 핵심 규칙 파일 복사 중...
if exist "%SOURCE_DIR%\.cursor\rules\*.mdc" (
    for %%F in ("%SOURCE_DIR%\.cursor\rules\*.mdc") do (
        if not exist "%TARGET_DIR%\.cursor\rules\%%~nxF" (
            copy "%%F" "%TARGET_DIR%\.cursor\rules\" >nul
            echo - %%~nxF 복사됨
        )
    )
) else (
    echo - 소스 디렉토리에 .mdc 파일이 없습니다
)

REM docs 폴더 생성 및 workflow-rules.md 문서 생성
echo 📝 docs 폴더 생성 중...
if not exist "%TARGET_DIR%\docs\" (
    mkdir "%TARGET_DIR%\docs"
    echo - docs 폴더 생성됨
)
(
    echo # Cursor 워크플로우 규칙
    echo,
    echo 이 프로젝트는 [cursor-auto-rules-agile-workflow](https://github.com/bmadcode/cursor-auto-rules-agile-workflow)의 자동 규칙 생성기를 사용하도록 업데이트되었습니다.
    echo,
    echo ^> **참고**: 이 스크립트는 템플릿 규칙을 최신 버전으로 업데이트하기 위해 언제든지 안전하게 다시 실행할 수 있습니다^. 생성한 사용자 지정 규칙에는 영향을 주거나 덮어쓰지 않습니다^.
    echo,
    echo ## 핵심 기능
    echo,
    echo - 자동화된 규칙 생성
    echo - 표준화된 문서 형식
    echo - AI 동작 제어 및 최적화
    echo - 유연한 워크플로우 통합 옵션
    echo,
    echo ## 워크플로우 통합 옵션
    echo,
    echo ### 1^. 자동 규칙 적용 (권장)
    echo 핵심 워크플로우 규칙은 ^.cursor/rules/에 자동으로 설치됩니다:
    echo - `901-prd^.mdc` - 제품 요구사항 문서 표준
    echo - `902-arch^.mdc` - 아키텍처 문서 표준
    echo - `903-story^.mdc` - 사용자 스토리 표준
    echo - `801-workflow-agile^.mdc` - 완전한 애자일 워크플로우 (선택 사항)
    echo,
    echo 이러한 규칙은 해당 파일 유형으로 작업할 때 자동으로 적용됩니다^.
    echo,
    echo ### 2^. 메모장 기반 워크플로우
    echo 더 유연한 접근 방식을 위해 `xnotes/`의 템플릿을 사용하세요:
    echo 1^. Cursor 옵션에서 메모장 활성화
    echo 2^. 새 메모장 생성 (예: "agile")
    echo 3^. `xnotes/workflow-agile^.md`에서 내용 복사
    echo 4^. 대화에서 `@메모장-이름` 사용
    echo,
    echo ^> **팁:** 메모장 접근 방식은 다음에 이상적입니다:
    echo ^> - 초기 프로젝트 설정
    echo ^> - 스토리 구현
    echo ^> - 집중 개발 세션
    echo ^> - 컨텍스트 오버헤드 감소
    echo,
    echo ## 시작하기
    echo,
    echo 1^. `xnotes/`의 템플릿 검토
    echo 2^. 선호하는 워크플로우 접근 방식 선택
    echo 3^. 자신감을 가지고 AI 사용 시작!
    echo,
    echo 데모 및 튜토리얼은 다음을 방문하세요: [BMad Code 비디오](https://youtube^.com/bmadcode)
) > "%TARGET_DIR%\docs\workflow-rules.md"
echo - workflow-rules.md 생성됨

REM .gitignore 업데이트
echo 📝 .gitignore 업데이트 중...
if exist "%TARGET_DIR%\.gitignore" (
    findstr /L /C:".cursor/rules/_*.mdc" "%TARGET_DIR%\.gitignore" >nul
    if errorlevel 1 (
        (
            echo,
            echo # 개인 사용자 커서 규칙
            echo .cursor/rules/_*.mdc
            echo .cursor/rules/
            echo Cursor/rules/
            echo,
            echo # 문서 및 템플릿
            echo xnotes/
            echo docs/
        ) >> "%TARGET_DIR%\.gitignore"
        echo - .gitignore 업데이트됨
    ) else (
        echo - .gitignore 이미 업데이트됨
    )
) else (
    (
        echo # 개인 사용자 커서 규칙
        echo .cursor/rules/_*.mdc
        echo .cursor/rules/
        echo Cursor/rules/
        echo,
        echo # 문서 및 템플릿
        echo xnotes/
        echo docs/
    ) > "%TARGET_DIR%\.gitignore"
    echo - .gitignore 생성됨
)

REM 메모장 템플릿 설치
echo 📝 메모장 템플릿 설정 중...
if not exist "%TARGET_DIR%\xnotes\" (
    mkdir "%TARGET_DIR%\xnotes"
    echo - xnotes 폴더 생성됨
)
if exist "%SOURCE_DIR%\xnotes\*.*" (
    xcopy "%SOURCE_DIR%\xnotes\*.*" "%TARGET_DIR%\xnotes\" /E /I /Y >nul
    echo - 템플릿 파일 복사됨
) else (
    echo - 소스 디렉토리에 xnotes 템플릿이 없습니다
)

REM Cursor 자동 규칙 추가를 위한 .cursor/settings.json 생성 또는 업데이트
echo ⚙️ Cursor 자동 규칙 설정 중...
if not exist "%TARGET_DIR%\.cursor\" (
    mkdir "%TARGET_DIR%\.cursor"
    echo - .cursor 폴더 생성됨
)

set "SETTINGS_FILE=%TARGET_DIR%\.cursor\settings.json"
set "TEMP_FILE=%TARGET_DIR%\.cursor\settings_temp.json"

if exist "%SETTINGS_FILE%" (
    REM 기존 settings.json 파일이 있는 경우 업데이트
    type "%SETTINGS_FILE%" > "%TEMP_FILE%"
    
    REM rules 경로 추가 확인
    findstr /C:"\"rules\": \[" "%SETTINGS_FILE%" >nul
    if errorlevel 1 (
        REM rules 항목이 없는 경우 추가
        powershell -Command "(Get-Content '%TEMP_FILE%') -replace '(\{)', '$1\n  \"rules\": [\"xnotes/*.md\"],' | Set-Content '%SETTINGS_FILE%'"
        echo - settings.json에 rules 항목 추가됨
    ) else (
        REM rules 항목이 있는 경우 xnotes/*.md 추가 확인
        findstr /C:"xnotes/*.md" "%SETTINGS_FILE%" >nul
        if errorlevel 1 (
            REM xnotes/*.md가 없는 경우 추가
            powershell -Command "(Get-Content '%TEMP_FILE%') -replace '(\"rules\": \[)', '$1\"xnotes/*.md\",' | Set-Content '%SETTINGS_FILE%'"
            echo - settings.json에 xnotes/*.md 항목 추가됨
        ) else (
            echo - settings.json 이미 업데이트됨
        )
    )
) else (
    REM settings.json 파일이 없는 경우 새로 생성
    (
        echo {
        echo   "rules": ["xnotes/*.md"]
        echo }
    ) > "%SETTINGS_FILE%"
    echo - settings.json 생성됨
)

if exist "%TEMP_FILE%" del "%TEMP_FILE%"

REM .cursorignore 업데이트
echo 📝 .cursorignore 업데이트 중...
if exist "%TARGET_DIR%\.cursorignore" (
    findstr /L /C:"xnotes/" "%TARGET_DIR%\.cursorignore" >nul
    if errorlevel 1 (
        (
            echo,
            echo # 프로젝트 노트 및 템플릿
            echo xnotes/
        ) >> "%TARGET_DIR%\.cursorignore"
        echo - .cursorignore 업데이트됨
    ) else (
        echo - .cursorignore 이미 업데이트됨
    )
) else (
    (
        echo # 프로젝트 노트 및 템플릿
        echo xnotes/
    ) > "%TARGET_DIR%\.cursorignore"
    echo - .cursorignore 생성됨
)

REM test.txt 파일 삭제 (존재하는 경우)
if exist "%TARGET_DIR%\test.txt" (
    del "%TARGET_DIR%\test.txt"
)

echo,
echo ✨ 배포 완료!
echo 핵심 규칙: %TARGET_DIR%\.cursor\rules\
echo 메모장 템플릿: %TARGET_DIR%\xnotes\
echo 문서: %TARGET_DIR%\docs\workflow-rules.md
echo .gitignore 및 .cursorignore 업데이트됨
echo xnotes/*.md에서 자동으로 규칙을 추가하도록 Cursor 구성됨
if "%KOREAN_FOUND%"=="true" echo 한국어 마크다운 파일이 .mdc로 변환되어 .cursor\rules 폴더에 저장됨
echo,
echo 다음 단계:
echo 1^. docs\workflow-rules^.md의 문서 검토
echo 2^. 선호하는 워크플로우 접근 방식 선택
echo 3^. 유연한 워크플로우 옵션을 사용하는 경우 Cursor 메모장 활성화
echo 4^. 새 프로젝트를 시작하려면 xnotes\project-idea-prompt^.md를 템플릿으로 사용하여
echo    AI 에이전트에 보낼 초기 메시지 작성

endlocal

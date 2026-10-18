@echo off
chcp 65001 >nul
title 大肥鱼指针 · FeiyuCursor 一键安装程序
cd /d "%~dp0"

echo ========================================================
echo       ✨ 大肥鱼指针 · FeiyuCursor 一键安装与配置 ✨
echo ========================================================
echo.

:: 1. 优先部署到当前用户专属目录（100%% 无需管理员权限，彻底杜绝权限不足和“文件已损坏”错误）
set "USER_TARGET=%LOCALAPPDATA%\Cursors\FeiyuCursor"
if not exist "%USER_TARGET%" mkdir "%USER_TARGET%"

echo [1/3] 正在复制指针文件到用户目录:
echo       %USER_TARGET% ...
copy /Y "%~dp0feiyu_*.cur" "%USER_TARGET%\" >nul
copy /Y "%~dp0feiyu_*.ani" "%USER_TARGET%\" >nul

:: 2. 如果当前有管理员权限，也同步备份一份到 C:\Windows\Cursors\FeiyuCursor
net session >nul 2>&1
if %errorlevel% equ 0 (
    set "SYS_TARGET=%SystemRoot%\Cursors\FeiyuCursor"
    if not exist "%SYS_TARGET%" mkdir "%SYS_TARGET%"
    copy /Y "%~dp0feiyu_*.cur" "%SYS_TARGET%\" >nul
    copy /Y "%~dp0feiyu_*.ani" "%SYS_TARGET%\" >nul
    echo [✓] 管理员权限检测通过，已同步备份到系统目录。
)

echo.
echo [2/3] 正在写入 Windows 鼠标指针方案注册表 ...

set "SCHEME_VAL=%USER_TARGET%\feiyu_arrow.cur,%USER_TARGET%\feiyu_help.cur,%USER_TARGET%\feiyu_appstart.ani,%USER_TARGET%\feiyu_busy.ani,%USER_TARGET%\feiyu_cross.cur,%USER_TARGET%\feiyu_ibeam.cur,%USER_TARGET%\feiyu_pen.cur,%USER_TARGET%\feiyu_no.cur,%USER_TARGET%\feiyu_sizens.cur,%USER_TARGET%\feiyu_sizewe.cur,%USER_TARGET%\feiyu_sizenwse.cur,%USER_TARGET%\feiyu_sizenesw.cur,%USER_TARGET%\feiyu_sizeall.cur,%USER_TARGET%\feiyu_up.cur,%USER_TARGET%\feiyu_hand.cur,%USER_TARGET%\feiyu_pin.cur,%USER_TARGET%\feiyu_person.cur"

reg add "HKCU\Control Panel\Cursors\Schemes" /v "大肥鱼指针" /t REG_EXPAND_SZ /d "%SCHEME_VAL%" /f >nul
reg add "HKCU\Control Panel\Cursors\Schemes" /v "FeiyuCursor · 大肥鱼指针" /t REG_EXPAND_SZ /d "%SCHEME_VAL%" /f >nul

:: 预设当前指针属性
reg add "HKCU\Control Panel\Cursors" /v "Arrow" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_arrow.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "Help" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_help.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "AppStarting" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_appstart.ani" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "Wait" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_busy.ani" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "Crosshair" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_cross.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "IBeam" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_ibeam.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "NWPen" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_pen.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "No" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_no.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "SizeNS" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_sizens.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "SizeWE" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_sizewe.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "SizeNWSE" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_sizenwse.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "SizeNESW" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_sizenesw.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "SizeAll" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_sizeall.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "UpArrow" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_up.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "Hand" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_hand.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "Pin" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_pin.cur" /f >nul
reg add "HKCU\Control Panel\Cursors" /v "Person" /t REG_EXPAND_SZ /d "%USER_TARGET%\feiyu_person.cur" /f >nul

echo.
echo ========================================================
echo  [✓] 大肥鱼指针安装成功！
echo  即将打开鼠标属性面板，请在方案中选择「大肥鱼指针」并点击「确定」！
echo ========================================================
echo.
timeout /t 2 >nul
start main.cpl ,,1

@echo off
chcp 65001 >nul
title 大肥鱼指针 · FeiyuCursor 一键安装程序
echo ========================================================
echo       ✨ 大肥鱼指针 · FeiyuCursor 一键安装与配置 ✨
echo ========================================================
echo.
echo 正在复制指针文件到系统目录 C:\Windows\Cursors\FeiyuCursor ...

set TARGET_DIR=%SystemRoot%\Cursors\FeiyuCursor
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

copy /Y feiyu_*.cur "%TARGET_DIR%\" >nul
copy /Y feiyu_*.ani "%TARGET_DIR%\" >nul

echo 正在注册指针方案到系统注册表 ...
reg add "HKCU\Control Panel\Cursors\Schemes" /v "大肥鱼指针" /t REG_EXPAND_SZ /d "%TARGET_DIR%\feiyu_arrow.cur,%TARGET_DIR%\feiyu_help.cur,%TARGET_DIR%\feiyu_appstart.ani,%TARGET_DIR%\feiyu_busy.ani,%TARGET_DIR%\feiyu_cross.cur,%TARGET_DIR%\feiyu_ibeam.cur,%TARGET_DIR%\feiyu_pen.cur,%TARGET_DIR%\feiyu_no.cur,%TARGET_DIR%\feiyu_sizens.cur,%TARGET_DIR%\feiyu_sizewe.cur,%TARGET_DIR%\feiyu_sizenwse.cur,%TARGET_DIR%\feiyu_sizenesw.cur,%TARGET_DIR%\feiyu_sizeall.cur,%TARGET_DIR%\feiyu_up.cur,%TARGET_DIR%\feiyu_hand.cur,%TARGET_DIR%\feiyu_pin.cur,%TARGET_DIR%\feiyu_person.cur" /f >nul

reg add "HKCU\Control Panel\Cursors\Schemes" /v "FeiyuCursor · 大肥鱼指针" /t REG_EXPAND_SZ /d "%TARGET_DIR%\feiyu_arrow.cur,%TARGET_DIR%\feiyu_help.cur,%TARGET_DIR%\feiyu_appstart.ani,%TARGET_DIR%\feiyu_busy.ani,%TARGET_DIR%\feiyu_cross.cur,%TARGET_DIR%\feiyu_ibeam.cur,%TARGET_DIR%\feiyu_pen.cur,%TARGET_DIR%\feiyu_no.cur,%TARGET_DIR%\feiyu_sizens.cur,%TARGET_DIR%\feiyu_sizewe.cur,%TARGET_DIR%\feiyu_sizenwse.cur,%TARGET_DIR%\feiyu_sizenesw.cur,%TARGET_DIR%\feiyu_sizeall.cur,%TARGET_DIR%\feiyu_up.cur,%TARGET_DIR%\feiyu_hand.cur,%TARGET_DIR%\feiyu_pin.cur,%TARGET_DIR%\feiyu_person.cur" /f >nul

echo.
echo [✓] 大肥鱼指针安装成功！即将打开鼠标属性面板...
echo 请在弹出的设置窗口中，「方案」下拉菜单直接选择「大肥鱼指针」，然后点击「确定」或「应用」即可！
echo.
timeout /t 2 >nul
start main.cpl ,,1

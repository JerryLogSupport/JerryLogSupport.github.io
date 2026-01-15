@echo off
cd /d d:\Documents\GitHub\JerryLogSupport.github.io   REM ← 把这里改成你的仓库实际路径
git add --all
git commit -m "自动更新 Excel - %date% %time%" || exit /b 0   REM 如果没变化就跳过
git push origin main
echo 更新完成！
pause
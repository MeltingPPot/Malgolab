Set-Location cpp

if(-not(Test-Path build)){mkdir build}

Set-Location build

cmake .. -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

Set-Location ../..

# 新增算法库文件后应该重新运行此文件
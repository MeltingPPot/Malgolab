Set-Localtion cpp

if(-not(Test-Path build)){mkdir build}

Set-Localtion build

cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release

Set-Localtion ../..
# 新增算法库文件后应该重新运行此文件
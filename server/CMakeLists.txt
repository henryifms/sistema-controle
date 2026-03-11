cmake_minimum_required(VERSION 3.10)

project(teacher_server)

set(CMAKE_CXX_STANDARD 17)

add_executable(teacher_server
    src/main.cpp
    src/network.cpp
)

target_include_directories(teacher_server PRIVATE
    src
    ../shared
)

target_link_libraries(teacher_server
    ws2_32
)

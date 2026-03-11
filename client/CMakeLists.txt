cmake_minimum_required(VERSION 3.10)

project(student_client)

set(CMAKE_CXX_STANDARD 17)

add_executable(student_client
    src/main.cpp
    src/keyboard.cpp
    src/network.cpp
)

target_include_directories(student_client PRIVATE
    src
    ../shared
)

target_link_libraries(student_client
    ws2_32
)

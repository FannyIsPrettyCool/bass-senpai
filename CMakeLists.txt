cmake_minimum_required(VERSION 3.15)
project(bass-senpai VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add compile options
add_compile_options(-Wall -Wextra -pedantic)

# Find required packages
find_package(CURL REQUIRED)
find_package(Threads REQUIRED)

# Include FetchContent for dependencies
include(FetchContent)

# Fetch nlohmann/json for JSON parsing
FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(json)

# Fetch stb_image for image processing
FetchContent_Declare(
    stb
    GIT_REPOSITORY https://github.com/nothings/stb.git
    GIT_TAG master
)
FetchContent_MakeAvailable(stb)

# Create executable
add_executable(bass-senpai
    src/main.cpp
    src/mpris_client.cpp
    src/artwork_handler.cpp
    src/terminal_ui.cpp
    src/bass_senpai.cpp
)

# Include directories
target_include_directories(bass-senpai PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${stb_SOURCE_DIR}
)

# Link libraries
target_link_libraries(bass-senpai PRIVATE
    nlohmann_json::nlohmann_json
    CURL::libcurl
    Threads::Threads
)

# Install target
install(TARGETS bass-senpai DESTINATION bin)

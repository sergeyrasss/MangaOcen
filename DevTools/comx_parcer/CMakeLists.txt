cmake_minimum_required(VERSION 3.16)
project(QtNetworkExample)

# Настройка Qt6 (или Qt5)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

# Поиск Qt6 (если не найдено, попробуйте Qt5)
find_package(Qt6 REQUIRED COMPONENTS Core Network)

# Создание исполняемого файла
add_executable(${PROJECT_NAME} main.cpp)

# Подключение Qt-модулей
target_link_libraries(${PROJECT_NAME}
    PRIVATE
        Qt6::Core
        Qt6::Network
)

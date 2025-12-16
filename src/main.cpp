#include "bass_senpai.hpp"
#include <iostream>
#include <string>
#include <cstring>

void print_usage(const char* program_name) {
    std::cout << "bass-senpai - Terminal music status viewer with album artwork\n\n";
    std::cout << "Usage: " << program_name << " [OPTIONS]\n\n";
    std::cout << "Options:\n";
    std::cout << "  --interval <seconds>  Update interval in seconds (default: 1.0)\n";
    std::cout << "  --version            Show version information\n";
    std::cout << "  --help               Show this help message\n\n";
    std::cout << "Examples:\n";
    std::cout << "  " << program_name << "              Start with default 1 second update interval\n";
    std::cout << "  " << program_name << " --interval 2  Update every 2 seconds\n\n";
    std::cout << "Requirements:\n";
    std::cout << "  - playerctl must be installed for MPRIS support\n";
    std::cout << "  - Kitty terminal recommended for pixel-perfect album artwork\n";
    std::cout << "  - Falls back to colored text-art in other terminals\n";
}

void print_version() {
    std::cout << "bass-senpai 1.0.0\n";
}

int main(int argc, char* argv[]) {
    double interval = 1.0;
    
    // Parse command-line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        } else if (arg == "--version" || arg == "-v") {
            print_version();
            return 0;
        } else if (arg == "--interval") {
            if (i + 1 < argc) {
                try {
                    interval = std::stod(argv[++i]);
                    if (interval < 0.1) {
                        std::cerr << "Error: Update interval must be at least 0.1 seconds\n";
                        return 1;
                    }
                } catch (...) {
                    std::cerr << "Error: Invalid interval value\n";
                    return 1;
                }
            } else {
                std::cerr << "Error: --interval requires a value\n";
                return 1;
            }
        } else {
            std::cerr << "Error: Unknown argument: " << arg << "\n";
            print_usage(argv[0]);
            return 1;
        }
    }
    
    // Create and run application
    bass_senpai::BassSenpai app(interval);
    return app.run();
}

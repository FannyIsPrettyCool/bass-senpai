#include "mpris_client.hpp"
#include <array>
#include <memory>
#include <stdexcept>
#include <sstream>
#include <cstdio>

namespace bass_senpai {

MPRISClient::MPRISClient() : playerctl_available_(check_playerctl()) {}

bool MPRISClient::is_playerctl_available() const {
    return playerctl_available_;
}

bool MPRISClient::check_playerctl() {
    try {
        std::string result = execute_command({"playerctl", "--version"});
        return !result.empty();
    } catch (...) {
        return false;
    }
}

std::string MPRISClient::execute_command(const std::vector<std::string>& args) {
    // Build command string with proper escaping
    std::string cmd;
    for (size_t i = 0; i < args.size(); ++i) {
        if (i > 0) cmd += " ";
        
        // Escape single quotes in the argument
        std::string arg = args[i];
        if (arg.find('\'') != std::string::npos || arg.find('{') != std::string::npos || 
            arg.find(' ') != std::string::npos) {
            // Use single quotes and escape any single quotes in the string
            std::string escaped;
            for (char c : arg) {
                if (c == '\'') {
                    escaped += "'\\''";
                } else {
                    escaped += c;
                }
            }
            cmd += "'" + escaped + "'";
        } else {
            cmd += arg;
        }
    }
    cmd += " 2>/dev/null";
    
    // Execute command
    std::array<char, 128> buffer;
    std::string result;
    std::unique_ptr<FILE, decltype(&pclose)> pipe(popen(cmd.c_str(), "r"), pclose);
    
    if (!pipe) {
        return "";
    }
    
    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr) {
        result += buffer.data();
    }
    
    // Remove trailing newline
    if (!result.empty() && result.back() == '\n') {
        result.pop_back();
    }
    
    return result;
}

std::optional<TrackMetadata> MPRISClient::get_metadata() {
    if (!playerctl_available_) {
        return std::nullopt;
    }
    
    try {
        std::string format = "{{artist}}|{{title}}|{{album}}|{{status}}|{{position}}|{{mpris:length}}|{{mpris:artUrl}}";
        std::string result = execute_command({
            "playerctl", "metadata", "--format", format
        });
        
        if (result.empty()) {
            return std::nullopt;
        }
        
        // Parse the pipe-delimited output
        std::vector<std::string> parts;
        std::stringstream ss(result);
        std::string part;
        
        while (std::getline(ss, part, '|')) {
            parts.push_back(part);
        }
        
        if (parts.size() < 7) {
            return std::nullopt;
        }
        
        TrackMetadata metadata;
        metadata.artist = parts[0].empty() ? "Unknown Artist" : parts[0];
        metadata.title = parts[1].empty() ? "Unknown Title" : parts[1];
        metadata.album = parts[2].empty() ? "Unknown Album" : parts[2];
        metadata.status = parts[3].empty() ? "Stopped" : parts[3];
        
        // Convert position and length from microseconds to seconds
        try {
            metadata.position = !parts[4].empty() ? std::stod(parts[4]) / 1000000.0 : 0.0;
            metadata.length = !parts[5].empty() ? std::stod(parts[5]) / 1000000.0 : 0.0;
        } catch (...) {
            metadata.position = 0.0;
            metadata.length = 0.0;
        }
        
        metadata.art_url = parts[6];
        
        return metadata;
    } catch (...) {
        return std::nullopt;
    }
}

std::string MPRISClient::get_playback_status() {
    if (!playerctl_available_) {
        return "Stopped";
    }
    
    try {
        std::string result = execute_command({"playerctl", "status"});
        return result.empty() ? "Stopped" : result;
    } catch (...) {
        return "Stopped";
    }
}

} // namespace bass_senpai

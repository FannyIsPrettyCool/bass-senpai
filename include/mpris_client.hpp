#pragma once

#include <string>
#include <vector>
#include <optional>
#include <map>

namespace bass_senpai {

struct TrackMetadata {
    std::string artist;
    std::string title;
    std::string album;
    std::string status;
    double position;  // in seconds
    double length;    // in seconds
    std::string art_url;
};

class MPRISClient {
public:
    MPRISClient();
    
    bool is_playerctl_available() const;
    std::optional<TrackMetadata> get_metadata();
    std::string get_playback_status();

private:
    bool playerctl_available_;
    bool check_playerctl();
    std::string execute_command(const std::vector<std::string>& args);
};

} // namespace bass_senpai

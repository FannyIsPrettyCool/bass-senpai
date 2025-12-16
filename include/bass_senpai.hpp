#pragma once

#include "mpris_client.hpp"
#include "artwork_handler.hpp"
#include "terminal_ui.hpp"
#include <memory>
#include <atomic>

namespace bass_senpai {

class BassSenpai {
public:
    explicit BassSenpai(double update_interval = 1.0);
    ~BassSenpai();
    
    int run();
    void stop();

private:
    double update_interval_;
    std::unique_ptr<MPRISClient> mpris_;
    std::unique_ptr<ArtworkHandler> artwork_;
    std::unique_ptr<TerminalUI> ui_;
    std::atomic<bool> running_;
    std::string last_track_id_;
    
    void update();
    std::string get_track_id(const std::optional<TrackMetadata>& metadata);
    
    static BassSenpai* instance_;
};

} // namespace bass_senpai

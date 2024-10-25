#include "pch.h"
#pragma warning(push)
#pragma warning(disable : 4996)
#include <sapi.h>
#include <sphelper.h>
#pragma warning(pop)
#include <string>
#include <thread>
#include <atomic>
#include <mutex>
#define SPSRS_DONE 3

class TextToSpeech {
public:
    TextToSpeech() : running(false) {
        HRESULT hr = CoInitialize(NULL);
        if (FAILED(hr)) {
            // Handle error
        }
        hr = ::CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL, IID_ISpVoice, (void**)&pVoice);
        if (FAILED(hr)) {
            // Handle error
        }
    }

    ~TextToSpeech() {
        Stop();
        if (pVoice) {
            pVoice->Release();
        }
        CoUninitialize();
    }

    void Speak(const std::wstring& text, float speed, float pitch, float volume, const std::wstring& voice) {
        Stop();  // Stop any previous speech
        running = true;

        std::thread([this, text, speed, pitch, volume, voice]() {
            {
                std::lock_guard<std::mutex> lock(mutex);
                if (voice != L"") {
                    ISpObjectToken* token;
                    if (SUCCEEDED(::SpFindBestToken(SPCAT_VOICES, voice.c_str(), nullptr, &token))) {
                        pVoice->SetVoice(token);
                        token->Release();
                    }
                }
                pVoice->SetRate(static_cast<long>(speed));
                pVoice->SetVolume(static_cast<USHORT>(volume));
                pVoice->Speak(text.c_str(), SPF_ASYNC, nullptr);
            }

            while (running) {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                SPVOICESTATUS status;
                pVoice->GetStatus(&status, nullptr);
                if (status.dwRunningState == SPSRS_DONE) {
                    break;
                }
            }
            running = false;
            // Safe to call DestroyTTS() from outside.
            }).detach();  // Ensure this is outside the lambda's closing brace
    }

    void Stop() {
        running = false;
        if (pVoice) {
            pVoice->Speak(L"", SPF_PURGEBEFORESPEAK, nullptr); // Stop speech
        }
    }

private:
    ISpVoice* pVoice = nullptr;
    std::atomic<bool> running;
    std::mutex mutex;
};

extern "C" __declspec(dllexport) TextToSpeech* CreateTTS() {
    return new TextToSpeech();
}

extern "C" __declspec(dllexport) void SpeakText(TextToSpeech* tts, const wchar_t* text, float speed, float pitch, float volume, const wchar_t* voice) {
    if (tts) {
        tts->Speak(text, speed, pitch, volume, voice);
    }
}

extern "C" __declspec(dllexport) void StopSpeech(TextToSpeech* tts) {
    if (tts) {
        tts->Stop();
    }
}

extern "C" __declspec(dllexport) void DestroyTTS(TextToSpeech* tts) {
    delete tts;
}

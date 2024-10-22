#include <windows.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static bool running = true;

__declspec(dllexport) void start_udp() {
    running = true;
}

__declspec(dllexport) void stop_udp() {
    running = false;
}

// Function to get the virtual key code for a character
int get_vk_code(char c, bool* shift_needed) {
    switch (c) {
        case '~': *shift_needed = true; return 0xC0; // VK_OEM_TILDE
        case '!': *shift_needed = true; return 0x31; // VK_1
        case '@': *shift_needed = true; return 0x32; // VK_2
        case '#': *shift_needed = true; return 0x33; // VK_3
        case '$': *shift_needed = true; return 0x34; // VK_4
        case '%': *shift_needed = true; return 0x35; // VK_5
        case '^': *shift_needed = true; return 0x36; // VK_6
        case '&': *shift_needed = true; return 0x37; // VK_7
        case '*': *shift_needed = true; return 0x38; // VK_8
        case '(': *shift_needed = true; return 0x39; // VK_9
        case ')': *shift_needed = true; return 0x30; // VK_0
        case '_': *shift_needed = true; return 0xBD; // VK_OEM_MINUS
        case '+': *shift_needed = true; return 0xBB; // VK_OEM_PLUS
        case '{': *shift_needed = true; return 0xDB; // VK_OEM_LEFTBRACKET
        case '}': *shift_needed = true; return 0xDD; // VK_OEM_RIGHTBRACKET
        case '|': *shift_needed = true; return 0xDC; // VK_OEM_PIPE
        case ':': *shift_needed = true; return 0xBA; // VK_OEM_COLON
        case '"': *shift_needed = true; return 0xDE; // VK_OEM_QUOTE
        case '<': *shift_needed = true; return 0xBC; // VK_OEM_COMMA
        case '>': *shift_needed = true; return 0xBE; // VK_OEM_PERIOD
        case '?': *shift_needed = true; return 0xBF; // VK_OEM_2
        default:
            // Handle alphabetic characters for capitalized input
            if (c >= 'A' && c <= 'Z') {
                *shift_needed = true;
                return VkKeyScan(c) & 0xFF; // Return the virtual key for uppercase letters
            } else {
                *shift_needed = false;
                return VkKeyScan(c) & 0xFF; // Return the virtual key for lowercase letters and others
            }
    }
}

__declspec(dllexport) void udp(const char* text, float delay_per_key, float word_delay_min, float word_delay_max) {
    running = true;

    char* text_copy = _strdup(text);
    if (text_copy == NULL) {
        return; // Handle memory allocation failure
    }

    DWORD delay_per_key_ms = (DWORD)(delay_per_key * 1000);
    DWORD word_delay_min_ms = (DWORD)(word_delay_min * 1000);
    DWORD word_delay_max_ms = (DWORD)(word_delay_max * 1000);

    bool shift_active = false;

    for (int i = 0; text_copy[i] != '\0' && running; ++i) {
        char char_to_type = text_copy[i];
        bool shift_needed;
        int key = get_vk_code(char_to_type, &shift_needed);

        // Handle Shift key state
        if (shift_needed && !shift_active) {
            keybd_event(VK_SHIFT, 0, 0, 0); // Press Shift
            shift_active = true;
        } else if (!shift_needed && shift_active) {
            keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0); // Release Shift
            shift_active = false;
        }

        keybd_event(key, 0, 0, 0); // Key down
        keybd_event(key, 0, KEYEVENTF_KEYUP, 0); // Key up

        // Release Shift if it was pressed for the current character
        if (shift_needed) {
            keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0); // Release Shift
            shift_active = false; // Reset the shift state
        }

        Sleep(delay_per_key_ms);

        if (char_to_type == ' ') {
            int word_delay = (int)(rand() % (word_delay_max_ms - word_delay_min_ms + 1) + word_delay_min_ms);
            Sleep(word_delay);
        }
    }

    if (shift_active) {
        keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0); // Release Shift
    }

    free(text_copy);
}

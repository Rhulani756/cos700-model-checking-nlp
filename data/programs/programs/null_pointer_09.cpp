// null_pointer_09.cpp
// Parses a simple "key=value" configuration line. If the line does not
// contain an '=' character, parsing fails and returns nullptr, but the
// caller does not check the result before using it.
#include <iostream>
#include <cstring>

struct ConfigEntry {
    char key[32];
    char value[32];
};

ConfigEntry* parseLine(const char* line) {
    const char* equalsSign = strchr(line, '=');
    if (equalsSign == nullptr) {
        return nullptr;
    }

    ConfigEntry* entry = new ConfigEntry();
    int keyLength = equalsSign - line;
    strncpy(entry->key, line, keyLength);
    entry->key[keyLength] = '\0';
    strcpy(entry->value, equalsSign + 1);
    return entry;
}

int main() {
    const char* badLine = "this line has no equals sign";

    ConfigEntry* entry = parseLine(badLine);

    std::cout << "Parsed key: " << entry->key << std::endl; // BUG: entry is nullptr

    return 0;
}

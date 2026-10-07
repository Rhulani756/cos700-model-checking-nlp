// frontend/src/app/settings/page.js
"use client";

import { useState, useEffect } from "react";
import { Load } from "@tauri-apps/plugin-store";
import { COLORS } from "../components/colors";
import Link from "next/link";

export default function Settings() {
  const [apiKey, setApiKey] = useState("");
  const [saved, setSaved] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    (async () => {
      const { Store } = await import("@tauri-apps/plugin-store");
      const store = await Store.load("settings.json");
      const existing = await store.get("gemini_api_key");
      if (existing) setApiKey(existing);
      setLoaded(true);
    })();
  }, []);

  const handleSave = async () => {
    const { Store } = await import("@tauri-apps/plugin-store");
    const store = await Store.load("settings.json");
    await store.set("gemini_api_key", apiKey);
    await store.save();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!loaded) return null;

  return (
    <div className="flex-1 min-h-0 flex flex-col bg-white font-sans">
      <header className="border-b-4" style={{ backgroundColor: COLORS.black, borderColor: COLORS.gold }}>
        <div className="px-12 py-8">
          <h1 className="text-2xl font-black text-white">Settings</h1>
        </div>
      </header>

      <main className="flex-1 max-w-md mx-auto px-6 py-12 w-full space-y-4">
        <label className="block text-sm font-medium" style={{ color: COLORS.black }}>
          Gemini API Key
        </label>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="AIza..."
          className="w-full border rounded-lg p-2 text-sm"
          style={{ borderColor: COLORS.gold }}
        />
        <button
          onClick={handleSave}
          className="px-4 py-2 rounded-lg text-white font-medium"
          style={{ backgroundColor: COLORS.blue }}
        >
          {saved ? "Saved!" : "Save"}
        </button>
        <p className="text-xs" style={{ color: COLORS.black + "99" }}>
          Get a free key at{" "}
          <a
            href="https://aistudio.google.com/apikey"
            target="_blank"
            rel="noopener noreferrer"
            className="underline"
            style={{ color: COLORS.blueDark }}
          >
            Google AI Studio
          </a>.
        </p>

        <Link href="/" className="inline-block text-sm underline" style={{ color: COLORS.blueDark }}>
          ← Back to app
        </Link>
      </main>
    </div>
  );
}
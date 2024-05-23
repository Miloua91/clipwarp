import { useEffect, useState } from "react";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { io } from "socket.io-client";
import settings from "../../../desktop-app/settings.txt";

interface Clip {
  clips_text: string;
  id: number;
  user_id: number;
}

export default function Collection() {
  const [clips, setClips] = useState<Clip[]>([]);
  const [port, setPort] = useState<number>();

  useEffect(() => {
    fetch(settings)
      .then((r) => r.text())
      .then((text) => {
        setPort(Number(text));
      });
  }, []);

  async function getClips() {
    if (port) {
      const response = await fetch(`http://192.168.1.13:${port + 1}/`);
      const data = await response.json();
      setClips(data);
    }
  }

  useEffect(() => {
    getClips();
  }, [port]);

  useEffect(() => {
    if (port) {
      const socket = io(`ws://192.168.1.13:${port + 1}`);

      socket.onAny((event) => {
        getClips();
      });

      return () => {
        socket.disconnect();
      };
    }
  }, [getClips, port]);

  useEffect(() => {
    if (port) {
      const websocket = new WebSocket(`ws://192.168.1.13:${port}/webapp`);
      websocket.onmessage = () => {
        getClips();
      };
    }
  }, [port]);

  async function deleteClip(clipId: number) {
    try {
      if (port) {
        const response = await fetch(
          `http://192.168.1.13:${port + 1}/delete/${clipId}`,
          {
            method: "DELETE",
          },
        );
        if (!response.ok) {
          throw new Error("Failed to delete clip");
        }
        getClips();
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function copyToClipboard(text: string) {
    try {
      await navigator.clipboard.writeText(text);
      console.log("Text copied to clipboard:", text);
    } catch (error) {
      console.error("Failed to copy text to clipboard:", error);
    }
  }

  const categorizeClips = () => {
    const categorized: { [key: string]: { id: number; content: string }[] } = {
      Text: [],
    };
    clips.forEach((clip) => {
      const urlRegex = /(https?:\/\/[^\s]+)/g;
      const match = clip.clips_text.match(urlRegex);
      if (match) {
        const url = new URL(match[0]);
        let domain = url.hostname.replace(/^www\./, "");
        domain = domain.replace(/\.com$/, "");
        if (!categorized[domain]) {
          categorized[domain] = [];
        }
        categorized[domain].push({ id: clip.id, content: match[0] });
      } else {
        categorized.Text.push({ id: clip.id, content: clip.clips_text });
      }
    });

    return categorized;
  };

  const renderTabsTriggers = () => {
    const categorizedClips = categorizeClips();
    return (
      <>
        {Object.keys(categorizedClips).map((category) => (
          <TabsTrigger key={category} value={category}>
            {category}
          </TabsTrigger>
        ))}
      </>
    );
  };

  const renderTabsContent = () => {
    const categorizedClips = categorizeClips();
    return (
      <ScrollArea className="w-full rounded-md border p-4 mt-2 h-[calc(100vh-156px)]">
        {Object.entries(categorizedClips).map(([category, clips]) => (
          <TabsContent key={category} value={category} className="w-full">
            {clips.reverse().map((clip, index) => (
              <div key={index}>
                {category === "Text" ? (
                  <div className="flex gap-1 justify-between">
                    <span className="break-all">{clip.content}</span>
                    <div className="flex flex-col gap-2">
                      <Button
                        variant="ghost"
                        onClick={() => copyToClipboard(clip.content)}
                      >
                        Copy
                      </Button>
                      <Button
                        onClick={() => deleteClip(clip.id)}
                        variant="ghost"
                        className="hover:bg-red-500 hover:text-white"
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-between">
                    <a
                      href={clip.content}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="break-all"
                    >
                      {clip.content}
                    </a>
                    <div className="flex flex-col gap-2">
                      <Button
                        variant="ghost"
                        onClick={() => copyToClipboard(clip.content)}
                      >
                        Copy
                      </Button>
                      <Button
                        onClick={() => deleteClip(clip.id)}
                        variant="ghost"
                        className="hover:bg-red-500 hover:text-white"
                      >
                        Delete
                      </Button>
                    </div>
                  </div>
                )}
                <Separator className="my-2" />
              </div>
            ))}
          </TabsContent>
        ))}
      </ScrollArea>
    );
  };

  return (
    <Tabs defaultValue="Text" className="text-white flex flex-col items-start">
      <TabsList className="max-w-[800px] flex-wrap flex flex-col overflow-x-auto overflow-y-clip">
        {renderTabsTriggers()}
      </TabsList>
      {renderTabsContent()}
    </Tabs>
  );
}

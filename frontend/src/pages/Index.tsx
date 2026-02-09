import { AppLayout } from '@/components/layout/AppLayout';
import { ChatTerminal } from '@/components/chat/ChatTerminal';
import { ChatHistory } from '@/components/history/ChatHistory';
import { CommandPalette } from '@/components/command/CommandPalette';
import { TarsRobot } from '@/components/ui/TarsRobot';

const Index = () => {
  return (
    <AppLayout>
      <ChatTerminal />
      <ChatHistory />
      <CommandPalette />
      <TarsRobot />
    </AppLayout>
  );
};

export default Index;

import { useState } from "react";
import Calendar from "./Calendar";
import EventFeed from "./EventFeed";
import DayDetail from "./DayDetail";
import Chat from "./Chat";

function App() {
  const [view, setView] = useState("calendar");
  const [selectedDate, setSelectedDate] = useState(null);

  return (
    <div style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>OnLo — Athens Events</h1>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={() => setView("calendar")}>Calendar</button>
        <button onClick={() => setView("feed")} style={{ marginLeft: "8px" }}>
          All Events
        </button>
        <button onClick={() => setView("chat")} style={{ marginLeft: "8px" }}>
          Chat
        </button>
      </div>

      {view === "calendar" && (
        <>
          <Calendar onDateClick={setSelectedDate} />
          {selectedDate && <DayDetail date={selectedDate} />}
        </>
      )}

      {view === "feed" && <EventFeed />}
      {view === "chat" && <Chat />}
    </div>
  );
}

export default App;

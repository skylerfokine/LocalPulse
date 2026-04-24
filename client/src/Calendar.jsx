import { useState, useEffect } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";

function Calendar({ onDateClick }) {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/events")
      .then((res) => res.json())
      .then((apiEvents) => {
        const calendarEvents = apiEvents.map((event) => ({
          id: event.id,
          title: event.title,
          start: event.time ? `${event.date}T${event.time}` : event.date,
          extendedProps: {
            location: event.location,
            description: event.description,
            cost_free: event.cost_free,
            cost_amount: event.cost_amount,
            category: event.category,
            source_url: event.source_url,
          },
        }));
        setEvents(calendarEvents);
      })
      .catch((err) => console.error("Failed to fetch events:", err));
  }, []);

  return (
    <FullCalendar
      plugins={[dayGridPlugin, interactionPlugin]}
      initialView="dayGridMonth"
      events={events}
      dateClick={(info) => onDateClick(info.dateStr)}
      height="auto"
    />
  );
}

export default Calendar;

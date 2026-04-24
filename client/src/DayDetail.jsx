import { useState, useEffect } from "react";

function DayDetail({ date }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:8000/events/${date}`)
      .then((res) => res.json())
      .then((data) => {
        setEvents(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch events:", err);
        setLoading(false);
      });
  }, [date]);

  if (loading) return <p>Loading...</p>;

  return (
    <div style={{ marginTop: "20px" }}>
      <h2>Events on {date}</h2>
      {events.length === 0 ? (
        <p>No events on this day.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {events.map((event) => (
            <li
              key={event.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: "8px",
                padding: "16px",
                marginBottom: "12px",
              }}
            >
              <h3 style={{ margin: "0 0 8px 0" }}>{event.title}</h3>
              {event.time && (
                <p style={{ margin: "4px 0" }}>
                  <strong>Time:</strong> {event.time}
                </p>
              )}
              {event.location && (
                <p style={{ margin: "4px 0" }}>
                  <strong>Location:</strong> {event.location}
                </p>
              )}
              {event.cost_free !== null && (
                <p style={{ margin: "4px 0" }}>
                  <strong>Cost:</strong>{" "}
                  {event.cost_free ? "Free" : `$${event.cost_amount}`}
                </p>
              )}
              {event.description && (
                <p style={{ margin: "8px 0 4px 0" }}>{event.description}</p>
              )}
              <a
                href={event.source_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                More info →
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default DayDetail;

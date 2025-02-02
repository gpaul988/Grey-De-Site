import { useEffect, useState } from "react";

interface Notification {
    id: string;
    message: string;
}

const Notifications = () => {
    const [notifications, setNotifications] = useState<Notification[]>([]);

    useEffect(() => {
        fetch("/api/notifications", {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
        })
            .then((res) => res.json())
            .then((data) => setNotifications(data));
    }, []);

    return (
        <div className="p-4 bg-white shadow-md rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Notifications</h2>
            {notifications.length === 0 ? (
                <p>No new notifications</p>
            ) : (
                <ul>
                    {notifications.map((notification) => (
                        <li key={notification.id} className="mb-2">
                            {notification.message}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Notifications;
const SESSION_KEY = "fox-dashboard-user";

const requireLogin = () => {
  if (sessionStorage.getItem(SESSION_KEY) !== "demo") location.replace("login.html");
};

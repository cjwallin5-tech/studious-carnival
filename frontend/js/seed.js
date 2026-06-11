/**
 * Seeds a small demo network through the public API.
 *
 * The shape is chosen to make every exercise interesting:
 *   - two tight clusters (alice..dave and erin..heidi) -> communities, clustering
 *   - ivan bridges the clusters                        -> shortest paths
 *   - judy is followed by almost everyone              -> PageRank hub
 *   - mallory follows a few people but has no followers -> recommendations
 *   - oscar has no edges at all                        -> a second component
 *
 * Idempotent: registering an existing user fails harmlessly and the follow
 * endpoint is a no-op when the edge already exists.
 */

const PASSWORD = "seed-password-123";

const USERS = [
  ["alice",   "Alice Park",    "cluster A"],
  ["bob",     "Bob Tran",      "cluster A"],
  ["carol",   "Carol Reyes",   "cluster A"],
  ["dave",    "Dave Kim",      "cluster A"],
  ["erin",    "Erin Walsh",    "cluster B"],
  ["frank",   "Frank Osei",    "cluster B"],
  ["grace",   "Grace Liu",     "cluster B"],
  ["heidi",   "Heidi Novak",   "cluster B"],
  ["ivan",    "Ivan Sorin",    "the bridge"],
  ["judy",    "Judy Ahmed",    "the hub"],
  ["mallory", "Mallory Quinn", "newcomer"],
  ["oscar",   "Oscar Bell",    "the loner"],
];

const FOLLOWS = [
  // cluster A — dense
  ["alice", "bob"], ["bob", "alice"],
  ["alice", "carol"], ["carol", "alice"],
  ["bob", "carol"], ["carol", "dave"],
  ["dave", "alice"], ["dave", "bob"],
  // cluster B — dense
  ["erin", "frank"], ["frank", "erin"],
  ["erin", "grace"], ["grace", "heidi"],
  ["heidi", "erin"], ["frank", "grace"],
  ["grace", "frank"], ["heidi", "frank"],
  // ivan bridges the clusters
  ["ivan", "alice"], ["ivan", "erin"],
  ["carol", "ivan"], ["frank", "ivan"],
  // judy the hub — followed widely, follows few
  ["alice", "judy"], ["bob", "judy"], ["carol", "judy"], ["dave", "judy"],
  ["erin", "judy"], ["frank", "judy"], ["grace", "judy"], ["ivan", "judy"],
  ["judy", "alice"], ["judy", "erin"],
  // mallory the newcomer — follows in, nobody follows back
  ["mallory", "judy"], ["mallory", "alice"], ["mallory", "bob"],
  // oscar: no edges (isolated component)
];

/**
 * @param {import("./api.js").Api} api
 * @param {(msg: string) => void} log
 */
export async function seedDemoNetwork(api, log) {
  log("seeding: registering users…");
  for (const [username, fullName, bio] of USERS) {
    await api.register({
      username,
      email: `${username}@example.com`,
      password: PASSWORD,
      full_name: fullName,
      bio,
    }); // 400 "already taken" is fine
  }

  log("seeding: logging in…");
  const tokens = new Map();
  for (const [username] of USERS) {
    const token = await api.login(username, PASSWORD);
    if (token) tokens.set(username, token);
  }
  if (tokens.size === 0) {
    throw new Error("seeding failed: could not log in as any demo user");
  }

  // username -> id, from the public user list
  const ids = new Map();
  for (const u of await api.allUsers()) ids.set(u.username, u.id);

  log("seeding: creating follows…");
  let made = 0;
  for (const [follower, followed] of FOLLOWS) {
    const token = tokens.get(follower);
    const targetId = ids.get(followed);
    if (!token || targetId === undefined) continue;
    const res = await api.follow(targetId, token);
    if (res.ok) made++;
  }
  log(`seeding done: ${USERS.length} users, ${made}/${FOLLOWS.length} follow edges in place.`);
}

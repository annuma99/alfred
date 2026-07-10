/**
 * The only file that knows your backend's URL or HTTP details.
 * Every component calls these functions instead of using fetch directly --
 * if the backend URL ever changes, this is the one place to update it.
 */

const API_URL = import.meta.env.VITE_API_URL;

async function request(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    throw new Error(`Request to ${path} failed: ${response.status}`);
  }
  return response.json();
}

export function getCrimePins(borough, range) {
  const params = new URLSearchParams({ range });
  if (borough) params.set("borough", borough);
  return request(`/crimes?${params.toString()}`);
}

export function getCrimeDetail(cmplntNum) {
  return request(`/crimes/${cmplntNum}`);
}

export function getBoroughs() {
  return request("/boroughs");
}

export function getBoroughBreakdown(borough) {
  return request(`/boroughs/${borough}/breakdown`);
}

import axios from 'axios'

export function getRealtimeFlow() {
  return axios.get('/api/realtime/flow').then(res => res.data)
}

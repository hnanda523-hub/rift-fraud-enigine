import axios from 'axios'

const BASE_URL = 'https://rift-fraud-backend.onrender.com'

export async function analyzeCSV(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await axios.post(`${BASE_URL}/analyze`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

  return response.data
}
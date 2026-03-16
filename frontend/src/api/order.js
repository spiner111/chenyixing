import request from './request'

export const createOrder = (data) => request.post('/orders', data)

export const getOrders = (params) => request.get('/orders', { params })

export const getOrderDetail = (id) => request.get(`/orders/${id}`)

export const cancelOrder = (id) => request.put(`/orders/${id}/cancel`)

export const payOrder = (id) => request.put(`/orders/${id}/pay`)

export const confirmOrder = (id) => request.put(`/orders/${id}/confirm`)

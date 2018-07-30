import {ApolloClient} from 'apollo-client'
import {HttpLink} from 'apollo-link-http'
import {ApolloLink, concat} from 'apollo-link'
import Cookie from 'js-cookie'
import {BatchHttpLink} from 'apollo-link-batch-http'
import {InMemoryCache} from 'apollo-cache-inmemory'
import {onError} from 'apollo-link-error'
import rootVue from './main'

// Настраиваем соединение в зависимости от среды
const production = process.env.NODE_ENV === 'production'
const opts = {
  // Для разработки необходимо указывать credentials: include так как порты серверов разные
  credentials: production ? 'same-origin' : 'include',
  // Для разработки используем локальный сервер на другом порту
  uri: production ? '/api_v1' : 'http://localhost:8000/api_v1'
}

/*
Для продакшена используем накопление запросов в один (batching) с макс. интервалом ожидания 50 мс
https://www.apollographql.com/docs/link/links/batch-http.html
*/
if (production) {
  opts['batchInterval'] = 50
}

const httpLink = production ? new BatchHttpLink(opts) : new HttpLink(opts)

const errorLink = onError(({graphQLErrors}) => {
  if (graphQLErrors && graphQLErrors.length > 0) {
    rootVue.$children[0].$refs.alarms.push(graphQLErrors[0].message)
  }
})

const csrfMiddleware = new ApolloLink((operation, forward) => {
  // Добавляем CSRF-токен к запросу
  operation.setContext({
    headers: {
      'X-CSRFToken': Cookie.get('csrftoken') || null
    }
  })
  return forward(operation)
})

const link = errorLink.concat(concat(csrfMiddleware, httpLink))

// Create the apollo client
const apolloClient = new ApolloClient({
  link: link,
  cache: new InMemoryCache()
})

export default apolloClient

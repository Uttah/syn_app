import gql from 'graphql-tag'

const tasksOnProjects = gql`
query ($paged: PagedInput!, $filters: TasksFilter) {
  tasksOnProjects(paged: $paged, filters: $filters){
    tasks {
      id
      name
      project {
        id
        number
        description
      }
    },
    totalCount  
  }
}`

const createNewTask = gql`
mutation ($input: AddTaskInput!) {
  addTask(input: $input){
    task {
      id
      name
      project {
        id
      }
    }  
  }
}`

const removeTask = gql`
mutation ($input: DeleteTaskInput!) {
  deleteTask(input: $input){
    result
  }
}`

const editTask = gql`
mutation ($input: EditTaskInput!) {
  editTask(input: $input){
    task {
      id
      name
      project {
        id
        number
        description
      }
    }
  }
}`

export {tasksOnProjects, createNewTask, removeTask, editTask}

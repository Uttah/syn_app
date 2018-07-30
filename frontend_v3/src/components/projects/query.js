import gql from 'graphql-tag'

const pagedProjects = gql`
query($paged: PagedInput!, $filters: ProjectsFilter){
  pagedProjects(paged: $paged, filters: $filters) {
    projects {
      id
      number
      dateCreated
      userCreated {
        id
        shortName
      }
      customer {
        id
        name
      }
      description
      manager {
        id
        shortName
      }
      comment
      gip {
        id
        shortName
      }
      state {
        id
        name
      }
      budget
      customer {
        id
        name
      }
      manager {
        id
        shortName
      }
    }
    totalCount
  }
}`

const allForFillSelect = gql`
query {
  allStates {
     id
     name
  }
  allClients {
    id
    name
  }
}`

const createProject = gql`
mutation($input: CreateProjectInput!) {
  createProject(input: $input) {
    project {
      id
    }
  }
}
`

const deleteProject = gql`
mutation($input: DeleteProjectInput!) {
  deleteProject(input: $input) {
    result
  }
}
`

const updateProject = gql`
mutation($input: UpdateProjectInput!) {
  updateProject(input: $input) {
    project {
      id
    }
  }
}
`

export {pagedProjects, allForFillSelect, createProject, deleteProject, updateProject}

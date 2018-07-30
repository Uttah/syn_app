import gql from 'graphql-tag'

const pagedLogisticsRequest = gql`
query ($paged: PagedInput!, $filters: LogisticsRequestFilter) {
  pagedLogisticsRequest (paged: $paged, filters: $filters) {
    logisticsRequests {
      id
      whoRequested {
        id
        shortName
      }
      whenRequested
      deadline
      responsible {
        id
        shortName
      }
      goal {
        id
        name
        project {
          id
          number
          description
        }
      }
      needAttention
      requestCompleted
    }
    totalCount
  }
}`

const pagedLogisticsRequestPosition = gql`
query ($paged: PagedInput!, $filters: LogisticsRequestPositionFilter) {
  pagedLogisticsRequestPosition (paged: $paged, filters: $filters) {
    logisticsRequestPositions {
      goodKind {
        id
        code
        name
        manufacturer {
          id
          name
        }
      }
      subRows {
        id
        expectedDate
        deadline
        orderDate
        count
        sumTransfer
        realInStock
        inStock {
          id
          count
          unit {
            id
            shortName
            restrictSum
          }
          available
        }
        unit {
          id
          shortName
          restrictSum
        }
        request {
          id
          responsible {
            id
            shortName
            avatar
          }
          goal {
            id
            project {
              id
              number
              description
            }
          }
        }
        task {
          id
          name
          responsible {
            id
            shortName
            avatar
          }
          files {
            id
            name
            kind
          }
        }
        number
        transferpositionSet {
          id
          count
          transferred
          good {
            location {
              id
            }
            unit {
              id
              shortName
            }
          }
          transferRequest {
            id
            readyToGo
            completed
            whoRequested {
              id
              shortName
            }
          }
        }
      }
    }
    totalCount
  }
}`

const pagedTransferRequests = gql`
query ($paged: PagedInput!, $filters: TransferRequestsFilter) {
  pagedTransferRequests (paged: $paged, filters: $filters) {
    transferRequests {
      id
      needAttention
      status
      whoRequested {
        id
        shortName
        avatar
      }
      where {
        id
        name
        project {
          id
          number
          description
        }
      }
      readyToGo
      creationDate
      worker {
        id
        shortName
        avatar
      }
      completed
    }
    totalCount
  }
}`

const transferRequest = gql`
query ($requestId: IntID!, $sortBy: String, $desc: Boolean) {
  transferRequest (requestId: $requestId, sortBy: $sortBy, desc: $desc) {
    transferRequest {
      id
      whoRequested {
        id
        shortName
      }
      where {
        id
        name
        project {
          id
          number
          description
        }
      }
      worker {
        id
        shortName
      }
      readyToGo
      creationDate
      completed
    }
    transferPositions {
      goodKind {
        id
        code
        name
        manufacturer {
          id
          name
        }
        goodGroup {
          id
          name
        }
      }
      subRows {
        id
        number
        serialNumber
        location {
          id
          name
          project {
            id
            number
          }
        }
        project {
          id
          number
          description
        }
        count
        transfer
        unit {
          id
          shortName
          restrictSum
        }
        allCount
      }
    }
  }
}`

const addWorkerInTransferRequest = gql`
mutation ($input: AddWorkerInTransferRequestInput!) {
  addWorkerInTransferRequest (input: $input) {
    result
  }
}`

const workerRefuseInTransferRequest = gql`
mutation ($input: WorkerRefuseInTransferRequestInput!) {
  workerRefuseInTransferRequest (input: $input) {
    result
  }
}`

const updateTransferPositions = gql`
mutation ($input: UpdateTransferPositionsInput!) {
  updateTransferPositions (input: $input) {
    result
  }
}`

const completedTransferRequest = gql`
mutation ($input: CompletedTransferRequestInput!) {
  completedTransferRequest (input: $input) {
    result
  }
}`

const deleteTransferRequestInTransfer = gql`
mutation ($input: DeleteTransferRequestInTransferInput!) {
  deleteTransferRequestInTransfer (input: $input) {
    result
  }
}`

const getLogisticsRequest = gql`
query ($id: IntID!) {
  getLogisticsRequest (id: $id) {
    id
    whoRequested {
      id
      avatar
      shortName
    }
    whenRequested
    deadline
    purpose
    reasonId
    project
    gipId
    readyForWork
    goal {
      id
      project {
        id
      }
    }
    responsible {
      id
      avatar
      shortName
    }
    location {
      id
    }
    logisticsrequestpositionSet {
      id
      number
      count
      transferred
      canTransfer
      inStock {
        id
        count
        available
        unit {
          id
          shortName
          restrictSum
        }
      }
      canceled
      transferpositionSet {
        count
        transferred
        transferRequest {
          id
          readyToGo
          completed
          whoRequested {
            id
            shortName
            avatar
          }
        }
        good {
          id
          unit {
            id
            shortName
          }
        }
      }
      goodKind {
        id
        code
        name
        goodGroup {
          id
          name
        }
        manufacturer {
          id
          name
        }
      }
      unit {
        id
        shortName
        restrictSum
      }
      task {
        id
        name
        responsible {
          id
          avatar
          shortName
        }
        createdDate
        workStarted
        transferRequest {
          id
          readyToGo
          completed
          transferpositionSet {
            id
          }
        }
        files {
          id
          kind
          name
        }
        transferred
        transferredWithReadyToGoFalse
        replacement
        taskCompleted
      }
      orderDate
      expectedDate
      deadline
      finishedDate
      canceledPosition {
        id
      }
    }
  }
}`

const transferRequestPositionInfo = gql`
query ($positionId: IntID!) {
  transferRequestPositionInfo (positionId: $positionId) {
    id
    whoRequested {
      id
      shortName
      avatar
    }
    where {
      id
    }
    readyToGo
    completed
    count
  }
}`

const goodLocationInfo = gql`
query ($positionId: IntID!) {
  goodLocationInfo (positionId: $positionId) {
    project {
      number
      gip {
        avatar
        shortName
      }
    }
    good {
      unit {
        shortName
      }
      count
    }
  }
}`

const addResponsibleInLogisticsRequest = gql`
mutation ($input: AddResponsibleInLogisticsRequestInput!) {
  addResponsibleInLogisticsRequest (input: $input) {
    result
  }
}`

const createTaskForPositions = gql`
mutation ($input: CreateTaskForPositionsInput!) {
  createTaskForPositions (input: $input) {
    result
  }
}`

const addPositionInLogisticsRequest = gql`
mutation ($input: AddPositionInLogisticsRequestInput!) {
  addPositionInLogisticsRequest (input: $input) {
    result
  }
}`

const replacePositionInLogisticsRequest = gql`
mutation ($input: ReplacePositionInLogisticsRequestInput!) {
  replacePositionInLogisticsRequest (input: $input) {
    result
  }
}`

const deletePositionFromTask = gql`
mutation ($input: DeletePositionFromTaskInput!) {
  deletePositionFromTask (input: $input) {
    result
  }
}`

const deletePositionFromLogisticsRequest = gql`
mutation ($input: DeletePositionFromLogisticsRequestInput!) {
  deletePositionFromLogisticsRequest (input: $input) {
    result
  }
}`

const refuseTask = gql`
mutation ($input: RefuseTaskInput!) {
  refuseTask (input: $input) {
    result
  }
}`

const takeTask = gql`
mutation ($input: TakeTaskInput!) {
  takeTask (input: $input) {
    result
  }
}`

const disbandTask = gql`
mutation ($input: DisbandTaskInput!) {
  disbandTask (input: $input) {
    result
  }
}`

const renameTask = gql`
mutation ($input: RenameTaskInput!) {
  renameTask (input: $input) {
    result {
      id
      name
      responsible {
        id
        avatar
        shortName
      }
      createdDate
      workStarted
      transferRequest {
        id
        readyToGo
        completed
        transferpositionSet {
          id
        }
      }
      files {
        id
        kind
        name
      }
      transferred
      transferredWithReadyToGoFalse
      replacement
      taskCompleted
    }  
  }
}`

const publishRequest = gql`
mutation ($input: PublishRequestInput!) {
  publishRequest (input: $input) {
    result
  }
}`

const createTransferPosition = gql`
mutation ($input: CreateTransferPositionInput!) {
  createTransferPosition (input: $input) {
    result
  }
}`

const changeReadyToGo = gql`
mutation ($input: ChangeReadyToGoInput!) {
  changeReadyToGo (input: $input) {
    result
  }
}`

const deleteTransferRequest = gql`
mutation ($input: DeleteTransferRequestInput!) {
  deleteTransferRequest (input: $input) {
    result
  }
}`

const transferAll = gql`
mutation ($input: TransferAllInput!) {
  transferAll (input: $input) {
    result
  }
}`

const editPosition = gql`
mutation ($input: EditPositionInput!) {
  editPosition (input: $input) {
    result {
      id
      number
      count
      transferred
      canTransfer
      inStock {
        id
        count
        available
        unit {
          id
          shortName
          restrictSum
        }
      }
      canceled
      transferpositionSet {
        count
        transferred
        transferRequest {
          id
          readyToGo
          completed
          whoRequested {
            id
            shortName
            avatar
          }
        }
        good {
          id
          unit {
            id
            shortName
          }
        }
      }
      goodKind {
        id
        code
        name
        goodGroup {
          id
          name
        }
        manufacturer {
          id
          name
        }
      }
      unit {
        id
        shortName
        restrictSum
      }
      task {
        id
        name
        responsible {
          id
          avatar
          shortName
        }
        createdDate
        workStarted
        transferRequest {
          id
          readyToGo
          completed
          transferpositionSet {
            id
          }
        }
        files {
          id
          kind
          name
        }
        transferred
        transferredWithReadyToGoFalse
        replacement
        taskCompleted
      }
      orderDate
      expectedDate
      deadline
      finishedDate
      canceledPosition {
        id
      }
    }
  }
}`

const uploadIncomingOfferFile = gql`
mutation ($input: UploadIncomingOfferFileInput!) {
  uploadIncomingOfferFile (input: $input) {
    result {
      name
      id
      kind
    }
  }
}`

const deleteIncomingOfferFile = gql`
mutation ($input: DeleteIncomingOfferFileInput!) {
  deleteIncomingOfferFile (input: $input) {
    result
  }
}`

const getSpecificationIdByLogistic = gql`
query ($logisticId: IntID!) {
  getSpecificationIdByLogistic (logisticId: $logisticId)
}`

export {
  pagedLogisticsRequest,
  pagedLogisticsRequestPosition,
  pagedTransferRequests,
  transferRequest,
  addWorkerInTransferRequest,
  workerRefuseInTransferRequest,
  updateTransferPositions,
  completedTransferRequest,
  deleteTransferRequestInTransfer,
  getLogisticsRequest,
  transferRequestPositionInfo,
  goodLocationInfo,
  addResponsibleInLogisticsRequest,
  createTaskForPositions,
  addPositionInLogisticsRequest,
  replacePositionInLogisticsRequest,
  deletePositionFromTask,
  deletePositionFromLogisticsRequest,
  refuseTask,
  takeTask,
  disbandTask,
  renameTask,
  publishRequest,
  createTransferPosition,
  changeReadyToGo,
  deleteTransferRequest,
  transferAll,
  editPosition,
  uploadIncomingOfferFile,
  deleteIncomingOfferFile,
  getSpecificationIdByLogistic
}

import gql from 'graphql-tag'

const tableQuery = gql`
query ($paged: PagedInput!, $filters: GoodsFilter) {
  pagedGoods (paged: $paged, filters: $filters) {
    goods {
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
      subRows{
        id
        count
        location {
          id
          name
          project {
            id
            number
          }
        }
        unit {
          id
          name
          shortName
        }
        project {
          id
          number
        }
        responsible {
          id
          shortName
        }
        note
        defect
      }
    }
    totalCount
  }
}`

const pagedGoodKinds = gql`
query ($paged: PagedInput! $filters: GoodKindsFilter) {
  pagedGoodKinds (paged: $paged, filters: $filters) {
    goodKinds {
      id
      code
      name
      manufacturer {
        id
        name
      }
      goodGroup {
        id
      }
      analogs {
        id
      }
      new
      mass
      gosts
      confirmed {
        id
        shortName
      }
      defaultUnit {
        id
        shortName
      }
    }
    totalCount
  }
}`

const units = gql`
query {
  allUnitsData: allUnits {
    id
    name
    shortName
  }
}`

const manufacturers = gql`
query {
  allManufacturerData: allManufacturers {
    id
    name
  }
}`

const goodKinds = gql`
query ($search: String, $require: [IntID], $checked: Boolean) {
  allGoodKinds (search: $search, require: $require, checked: $checked) {
    id
    gosts
    code
    name
    mass
    defaultUnit {
      id
      shortName
    }
    manufacturer {
      id
      name
    }
  }
}`

const createGood = gql`
mutation ($input: CreateGoodInput!) {
  createGood (input: $input) {
    good {
      id
      count
      unit {
        id
        name
        shortName
      }
      location {
        id
        name
        project {
          id
          number
        }
      }
      note
      defect
      project {
        id
      }
      goodKind {
        id
        code
        name
        manufacturer {
          id
          name
        }
      }
    }
  }
}`

const createWarehouse = gql`
mutation ($input: CreateWarehouseInput!) {
  createWarehouse (input: $input) {
    warehouse {
      id
      name
      project {
        id 
        number
      }
      user {
        id
        shortName
      }
    }
  }
}`

const createGoodKind = gql`
mutation ($input: CreateGoodKindInput!) {
  createGoodKind (input: $input) {
    goodKind {
      id
      code
      name
      manufacturer {
        id
        name
      }
      defaultUnit {
        id
        shortName
      }
    }
  }
}`

const createManufacturer = gql`
mutation ($input: CreateManufacturerInput!) {
  createManufacturer (input: $input) {
    result
  }
}`

const updateGood = gql`
mutation ($input: UpdateGoodInput!) {
  updateGood (input: $input) {
    good {
      id
      count
      unit {
        id
        name
        shortName
      }
      location {
        id
        name
        project {
          id
          number
        }
      }
      responsible {
        id
        shortName
      }
      note
      defect
      project {
        id
      }
      goodKind {
        id
        code
        name
        manufacturer {
          id
          name
        }
      }
    }
  }
}`

const deleteGood = gql`
mutation ($input: DeleteGoodInput!) {
  deleteGood (input: $input) {
    result
  }
}`

const updateGoodKind = gql`
mutation ($input: UpdateGoodKindInput!) {
  updateGoodKind (input: $input) {
    goodKind {
      id
      code
      name
      manufacturer {
        id
        name
     }
     defaultUnit {
        id
        shortName
      }
    }
  }
}
`

const updateGoodKindExsistCode = gql`
mutation ($input: UpdateGoodKindExsistCodeInput!) {
  updateGoodKindExsistCode (input: $input) {
    goodKind {
      id
      code
      name
      manufacturer {
        id
        name
      }
      defaultUnit {
        id
        shortName
      }
    }
  }
}
`

const deleteGoodKind = gql`
mutation ($input: DeleteGoodKindInput!) {
  deleteGoodKind (input: $input) {
    result
  }
}`

const changeWarehouse = gql`
mutation ($input: ChangeWarehouseInput!) {
  changeWarehouse (input: $input) {
    result
  }
}`

const confirmGoodKind = gql`
mutation ($input: ConfirmGoodKindInput!) {
  confirmGoodKind (input: $input) {
    result
  }
}
`

const pagedSpecification = gql`
query ($paged: PagedInput!) {
  pagedSpecification (paged: $paged) {
    specifications {
      id
      project {
        id
        number
        description
        state {
          id
          letter
        }
        gip {
          id
        }
      }
      pressmark
      objectName
      sectionName
      organization
      documentName
      state
      workersData
      dates
      approved
    }
    totalCount
  }
}`

const createSpecification = gql`
mutation ($input: CreateSpecificationInput!) {
  createSpecification(input: $input) {
    result
  }
}`

const changeSpecification = gql`
mutation ($input: ChangeSpecificationInput!) {
  changeSpecification(input: $input) {
    result
  }
}`

const deleteSpecification = gql`
mutation ($input: DeleteSpecificationInput!) {
  deleteSpecification(input: $input) {
    result
  }
}`

const specificationsPositions = gql`
query ($filters: IntID) {
  specificationsPositions (filters: $filters) { 
    id
    groupingName
    descriptionInfo
    positionalDesignation
    unit {
      id
      shortName
    }
    count
    positionInTable
    goodKind {
      id
      gosts
      code
      name
      mass
      manufacturer {
        id
        name
      }
      new
    }
    specification {
      id
    }
    note
  }
}`

const allUnits = gql`
query  {
  allUnits {
    id
    name
    shortName
  }
}`

const createSpecificationPosition = gql`
mutation ($input: CreateSpecificationPositionInput!) {
  createSpecificationPosition(input: $input) {
    result
  }
}`

const changeSpecificationsPositions = gql`
mutation ($input: ChangeSpecificationsPositionsInput!) {
  changeSpecificationsPositions(input: $input) {
    result
  }
}`

const updateSpecificationPosition = gql`
mutation ($input: UpdateSpecificationPositionInput!) {
  updateSpecificationPosition(input: $input) {
    result
  }
}`

const deleteSpecificationPosition = gql`
mutation ($input: DeleteSpecificationPositionInput!) {
  deleteSpecificationPosition(input: $input) {
    result
  }
}`

const duplicateSpecificationPosition = gql`
mutation ($input: DuplicateSpecificationPositionInput!) {
  duplicateSpecificationPosition(input: $input) {
    result {
      id
      groupingName
      descriptionInfo
      positionalDesignation
      unit {
        id
        shortName
      }
      count
      positionInTable
      goodKind {
        id
        gosts
        code
        name
        mass
        manufacturer {
          id
          name
        }
        new
      }
      specification {
        id
      }
      note
    }
  }
}`

const descriptionsInfo = gql`
query ($filters: IntID!) {
  descriptionsInfo (filters: $filters)
}`

const createExcel = gql`
mutation($input: CreateExcelInput!) {
  createExcel (input: $input) {
    result
  }
}`

const specificationApproved = gql`
mutation ($input: SpecificationApprovedInput!) {
  specificationApproved (input: $input) {
    result
  }
}`

const cloneSpecification = gql`
mutation ($input: CloneSpecificationInput!) {
  cloneSpecification (input: $input) {
    result {
      id
      project {
        id
        number
        description
        state {
          id
          letter
        }
        gip {
          id
        }
      }
      pressmark
      objectName
      sectionName
      organization
      documentName
      state
      workersData
      dates
      approved
    }
  }
}`

const createApplication = gql`
mutation ($input: CreateApplicationInput!) {
  createApplication (input: $input) {
    result
  }
}`

const selectedSpecification = gql`
query ($specificationId: IntID) {
  selectedSpecification (specificationId: $specificationId) {
    id
    project {
      id
      number
      description
      state {
        id
        name
        letter
      }
      gip {
        id
        shortName
      }
    }
    pressmark
    documentName
    objectName
    organization
    sectionName
    state
    dates
    workersData
    approved
  }
}`

export {
  tableQuery,
  units,
  manufacturers,
  goodKinds,
  createGood,
  createWarehouse,
  createGoodKind,
  createManufacturer,
  updateGood,
  deleteGood,
  pagedGoodKinds,
  updateGoodKind,
  deleteGoodKind,
  changeWarehouse,
  confirmGoodKind,
  updateGoodKindExsistCode,
  pagedSpecification,
  createSpecification,
  changeSpecification,
  deleteSpecification,
  specificationsPositions,
  allUnits,
  createSpecificationPosition,
  changeSpecificationsPositions,
  updateSpecificationPosition,
  deleteSpecificationPosition,
  duplicateSpecificationPosition,
  descriptionsInfo,
  createExcel,
  specificationApproved,
  cloneSpecification,
  createApplication,
  selectedSpecification
}

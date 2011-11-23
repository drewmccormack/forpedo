program main
    use DynamicArrayIModule
    use DynamicArrayRModule
    use DynamicArrayIAModule
    implicit none
    type (DynamicArrayI)     :: iArray
    type (DynamicArrayR)     :: rArray
    type (DynamicArrayIA)    :: iaArray
    type (IntArray), pointer :: iaPtr
    integer i
    
    ! Array of reals
    call new(rArray)
    do i = 1, 20
        call append(rArray, 0.1)
    enddo
    print *, rArray%data(99)
    call delete(rArray)

    ! Array of integers
    call new(iArray)
    do i = 1, 500
        call append( iArray, 20 )
    enddo
    print *, iArray%data(450)
    call delete(iArray)

    ! Array of arrays
    call new(iaArray)
    do i = 1, 10
        iaArray%data(i)%array(10) = i * 10
        iaArray%data(i)%array(20) = i * 20
    enddo
    print *, iaArray%data(5)%array(10)
    print *, iaArray%data(5)%array(20)
    call delete(iaArray)

end program

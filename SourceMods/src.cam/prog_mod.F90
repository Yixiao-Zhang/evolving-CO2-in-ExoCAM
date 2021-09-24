! Module:
!   compute the global mean net TOA downwelling radiative flux
!   and then prognosticate parameters
! Author:
! Yixiao Zhang [yixiaozhang@pku.edu.cn]
module prog_mod

    use shr_kind_mod,       only: r8 => shr_kind_r8
    use ppgrid,             only: pcols
    use shr_const_mod,      only: shr_const_pi
    use shr_sys_mod,        only: shr_sys_abort
    use cam_logfile,        only: iulog
    use time_manager,     only: get_nstep

    implicit none
    private

    public prog_add_points
    public prog_do
    public prog_co2mmr

    ! [sum of weights, sum of weighted values]
    integer, parameter :: sum_size = 4
    real(r8), dimension(sum_size) :: world_sum = 0.0
    real(r8), parameter :: wght_expct = 4*shr_const_pi ! expected total weights

    real(r8), parameter :: co2_forcing = 5.35 ! W/m2
    integer, parameter :: relax_time = 0 ! unit: timestep
    integer, parameter :: efld_time = 48*240   ! unit: timestep

    real(r8), parameter :: init_co2mmr = 400.0e-6
    real(r8) :: prog_co2mmr = init_co2mmr
    real(r8) :: prog_logco2mmr = log(init_co2mmr)

    contains

    subroutine prog_add_points(state, fsnt, flnt)

        use physics_types,     only: physics_state
        use phys_grid,         only: get_wght_all_p

        ! Input
        type(physics_state), intent(in), target :: state
        real(r8), intent(inout) :: fsnt(pcols)
        real(r8), intent(inout) :: flnt(pcols)

        ! Local
        real(r8), dimension(pcols) :: wght
        real(r8) :: prog_rate
        integer :: lchnk, ncol
        integer :: i
        integer :: nstep

        lchnk = state%lchnk
        ncol = state%ncol

        nstep = get_nstep()

        call get_wght_all_p(lchnk, ncol, wght)

        if (nstep <= relax_time) then
            prog_rate = 0.0
        else
            prog_rate = 1.0/(co2_forcing*efld_time)
        endif

        do i = 1, ncol
            world_sum(1) = world_sum(1) + wght(i)

            world_sum(2) = world_sum(2) + &
                    wght(i)*(prog_logco2mmr+(flnt(i)-fsnt(i))*prog_rate)

            world_sum(3) = world_sum(3) + &
                    (wght(i)*flnt(i))

            world_sum(4) = world_sum(4) + &
                    (wght(i)*fsnt(i))

        enddo

    end subroutine prog_add_points

    subroutine prog_do()

        use parutilitiesmodule, only: sumop, parcollective
        use spmd_utils,       only: masterproc, mpicom


        call parcollective(mpicom, sumop, sum_size, world_sum)


        prog_logco2mmr = world_sum(2)/world_sum(1)
        prog_co2mmr = exp(prog_logco2mmr)


        ! check
        if (masterproc) then
            if (abs(world_sum(1)-wght_expct) > 1.0e-4) then
                call shr_sys_abort("The sum of weights is not 4pi.")
            endif
            write(iulog, *) "CO2 MMR:", prog_co2mmr*1.0e6, "ppm"
            write(iulog, *) "FLNT (W/m2)", world_sum(3)/world_sum(1)
            write(iulog, *) "FSNT (W/m2)", world_sum(4)/world_sum(1)
        endif

        world_sum = 0.0

    end subroutine prog_do

end module prog_mod

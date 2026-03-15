	.file	"query.c"
	.globl	_users_data
	.data
	.align 32
_users_data:
	.long	1
	.ascii "Alice\0"
	.space 94
	.long	2
	.ascii "Alice\0"
	.space 94
	.long	3
	.ascii "Alice\0"
	.space 94
	.globl	_users_count
	.align 4
_users_count:
	.long	3
	.def	___main;	.scl	2;	.type	32;	.endef
	.section .rdata,"dr"
LC0:
	.ascii "Alice\0"
LC1:
	.ascii "%d \0"
LC2:
	.ascii "%s \0"
	.text
	.globl	_main
	.def	_main;	.scl	2;	.type	32;	.endef
_main:
LFB13:
	.cfi_startproc
	pushl	%ebp
	.cfi_def_cfa_offset 8
	.cfi_offset 5, -8
	movl	%esp, %ebp
	.cfi_def_cfa_register 5
	andl	$-16, %esp
	subl	$32, %esp
	call	___main
	movl	$0, 28(%esp)
	jmp	L2
L4:
	movl	28(%esp), %eax
	imull	$104, %eax, %eax
	addl	$_users_data, %eax
	movl	(%eax), %eax
	testl	%eax, %eax
	jle	L3
	movl	28(%esp), %eax
	imull	$104, %eax, %eax
	addl	$_users_data, %eax
	addl	$4, %eax
	movl	$LC0, 4(%esp)
	movl	%eax, (%esp)
	call	_strcmp
	testl	%eax, %eax
	jne	L3
	movl	28(%esp), %eax
	imull	$104, %eax, %eax
	addl	$_users_data, %eax
	movl	(%eax), %eax
	movl	%eax, 4(%esp)
	movl	$LC1, (%esp)
	call	_printf
	movl	28(%esp), %eax
	imull	$104, %eax, %eax
	addl	$_users_data, %eax
	addl	$4, %eax
	movl	%eax, 4(%esp)
	movl	$LC2, (%esp)
	call	_printf
	movl	$10, (%esp)
	call	_putchar
L3:
	addl	$1, 28(%esp)
L2:
	movl	_users_count, %eax
	cmpl	%eax, 28(%esp)
	jl	L4
	movl	$0, %eax
	leave
	.cfi_restore 5
	.cfi_def_cfa 4, 4
	ret
	.cfi_endproc
LFE13:
	.ident	"GCC: (MinGW.org GCC-6.3.0-1) 6.3.0"
	.def	_strcmp;	.scl	2;	.type	32;	.endef
	.def	_printf;	.scl	2;	.type	32;	.endef
	.def	_putchar;	.scl	2;	.type	32;	.endef

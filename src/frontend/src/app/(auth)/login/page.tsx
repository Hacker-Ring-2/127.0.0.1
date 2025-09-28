// LoginPage.tsx
'use client';

import React, { useState } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { toast } from 'sonner';
import { Loader, EyeOff, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';
import ApiServices from '@/services/ApiServices';
import { LoginFormData } from '@/types/auth-types';
import Cookies from 'js-cookie';
import { OtpPasswordResetDialog } from '../components/ResetPassword';
import Image from 'next/image';
const LoginPage: React.FC = () => {
  const [isLoading, setIsLoading] = React.useState(false);
  const [showPassword, setShowPassword] = React.useState(false);

  const [isOtpDialogOpen, setIsOtpDialogOpen] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>();

  const router = useRouter();

  // define each rule
  // const rules = {
  //   length: password.length >= 8,
  //   upper: /[A-Z]/.test(password),
  //   lower: /[a-z]/.test(password),
  //   number: /[0-9]/.test(password),
  //   special: /[@$!%*?&]/.test(password),
  // };

  // check if all rules are valid
  // const allValid = Object.values(rules).every(Boolean);

  const onSubmit: SubmitHandler<LoginFormData> = async (data) => {
    setIsLoading(true);
    try {
      const response = await ApiServices.login(data.email, data.password);
      toast.success('Login successful');
      Cookies.set('access_token', response.access_token);
      router.push('/');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      toast.error(
        error?.response?.data?.detail || 'Invalid email or password or account does not exist.'
      );
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="min-h-screen h-auto w-full flex flex-col justify-center py-12 sm:px-6 px-2 lg:px-8 overflow-auto bg-[var(--primary-main-bg)]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex justify-center items-center">
        <h1 className="text-center sm:text-[2rem] text-[1.5rem] font-normal align-self-stretch">
          <Image
            src="/images/login_logo.svg" // This path must be correct
            width={231}
            height={48}
            alt="logo"
          />
        </h1>
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md overflow-auto">
        <div className="sm:py-10 py-4 px-2 sm:px-10">
          <form noValidate className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {/* ——— Email Field ——— */}
            <div>
              <input
                type="email"
                placeholder="Email"
                className={`block w-full px-3 py-3 bg-[var(--primary-chart-bg)] border ${
                  errors.email ? 'border-red-500 focus:ring-red-500' : 'border-primary-100'
                } rounded-md shadow-sm placeholder-neutral-150 focus:outline-none focus:ring-2 focus:ring-[#4B9770] sm:text-sm transition-all duration-200`}
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address',
                  },
                })}
              />
              {errors.email && <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>}
            </div>

            {/* ——— Password Field + Validation List ——— */}
            <div className="w-full">
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Password"
                  className={cn(
                    'block w-full px-3 py-3 pr-10 bg-[var(--primary-chart-bg)] border rounded-md shadow-sm placeholder-neutral-150 focus:outline-none focus:ring-2 focus:ring-[#4B9770] sm:text-sm transition-all duration-200',
                    errors.password ? 'border-red-500 focus:ring-red-500 ' : 'border-primary-100'
                  )}
                  {...register('password', { required: 'Password is required' })}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  className="absolute inset-y-0 right-3 flex items-center"
                >
                  {!showPassword ? (
                    <EyeOff className="w-5 h-5 text-neutral-500" />
                  ) : (
                    <Eye className="w-5 h-5 text-neutral-500" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
              )}
              <div className="w-full text-right">
                <button
                  type="button"
                  onClick={() => setIsOtpDialogOpen(true)}
                  className="mt-1 text-sm hover:underline font-normal text-[#4B9770]"
                >
                  Forgot password
                </button>
              </div>
            </div>

            {/* ——— Submit Button ——— */}
            <div>
              <button
                disabled={isLoading}
                type="submit"
                className={cn(
                  'w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#4B9770] hover:bg-[#408160] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4B9770] disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                {isLoading && <Loader className="w-5 h-5 mr-2 animate-spin" />}
                Continue
              </button>
            </div>
          </form>

          {/* ——— Signup Link ——— */}
          <div className="mt-5 text-center">
            <p className="text-neutral-150">
              Don&apos;t have an account?{' '}
              <Link href="/signup" className="font-medium text-[#4B9770] hover:text-[#408160]">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>

      <OtpPasswordResetDialog open={isOtpDialogOpen} onOpenChange={setIsOtpDialogOpen} />
    </div>
  );
};

export default LoginPage;

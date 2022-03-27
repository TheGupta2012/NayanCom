import "./form.css";
import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useForm } from "react-hook-form";
import { Redirect } from 'react-router-dom';

function Form() {
    const [formreg, setFormreg] = useState(false);
    const {
        register,
        handleSubmit,
        formState: { errors },
        trigger,
    } = useForm();

    const onSubmit = (data) => {
        var myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        var raw = JSON.stringify({
            email: data.email,
            phone: data.phone,
        })
        console.log(raw);
        const options = {
            method: 'POST',
            headers: myHeaders,
            body: raw,
        }
        fetch('http://localhost:4000/api', options).then((response) => {
        }).catch((err) => console.log('error1236'));
        setFormreg(true);
    };

    if (formreg) {
        return <Redirect to="/processing" />
    }

    return (
        <div className="container pt-2">
            <div className="row justify-content-sm-center pt-5">
                <div className="col-sm-6 shadow round pb-3">
                    <h3 className="text-center pt-3 text-secondary">Register Here</h3>
                    <form onSubmit={handleSubmit(onSubmit)} >
                        <div className="form-group">
                            <label className="col-form-label">Email:</label>
                            <input
                                type="text"
                                className={`form-control ${errors.email && "invalid"}`}
                                {...register("email", {
                                    required: "Email is Required",
                                    pattern: {
                                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                        message: "Invalid email address",
                                    }
                                })}
                                onKeyUp={() => {
                                    trigger("email");
                                }}

                            />
                            {errors.email && (
                                <small className="text-danger">{errors.email.message}</small>
                            )}
                        </div>
                        <div className="form-group">
                            <label className="col-form-label">Phone:</label>
                            <input
                                type="text"
                                className={`form-control ${errors.phone && "invalid"}`}
                                {...register("phone", {
                                    required: "Phone is Required",
                                    pattern: {
                                        value: /^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$/,
                                        message: "Invalid phone no",
                                    },
                                })}
                                onKeyUp={() => {
                                    trigger("phone");
                                }}
                            />
                            {errors.phone && (
                                <small className="text-danger">{errors.phone.message}</small>
                            )}
                        </div>
                        <div className="row justify-content-center pt-2 mx-auto">
                            <button type="submit" className="btn btn-primary my-3" value="Submit" >
                                Submit
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default Form;

from typing import Any, Union

import numpy as np
from qcodes.instrument.visa import VisaInstrument
from qcodes.utils import validators as vals


class SP983C(VisaInstrument):
    def __init__(self, name: str, address: str, **kwargs: Any) -> None:
        super().__init__(name, address, terminator="\r\n", **kwargs)

        self.add_parameter(
            "gain",
            label="Gain",
            unit="V/A",
            set_cmd=self.set_gain,
            get_cmd=self.get_gain,
            vals=vals.Enum(1e5, 1e6, 1e7, 1e8, 1e9),
        )
        self.add_parameter(
            "fcut",
            unit="Hz",
            label="Filter Cut-Off Frequency",
            set_cmd=self.set_filter,
            get_cmd=self.get_filter,
            vals=vals.Enum(30, 100, 300, 1000, 3000, 30_000, 100_000, "FULL"),
        )
        self.add_parameter(
            "overload_status",
            label="Overload Status",
            set_cmd=None,
            get_cmd="GET O"
        )

    def set_gain(self, value: float) -> None:
        r = self.ask(f"SET G 1E{int(np.log10(value))}")
        if r != "OK":
            raise ValueError(f"Expected OK return but got: {r}")

    def get_gain(self) -> float:
        s = self.ask("GET G")
        r = s.split("Gain: ")[1]
        return float(r)

    def set_filter(self, value: Union[str, float]) -> None:
        r = self.ask(f"SET F {value}")
        if r != "OK":
            raise ValueError(f"Expected OK return but got: {r}")

    def get_filter(self) -> Union[str, float]:
        s = self.ask("GET F")
        r = s.split("Filter: ")[1]
        if r == "Full":
            return r.upper()
        elif r[-3::] == "kHz":
            return float(r[0:-3]) * 1e3
        elif r[-2::] == "Hz":
            return float(r[0:-2])
        else:
            raise ValueError(f"Could not interpret result. Got: {s}")
